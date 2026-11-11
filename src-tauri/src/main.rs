#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::io::{BufRead, BufReader};
use std::process::{Child, Command, Stdio};
use std::sync::{mpsc, Mutex};
use std::time::{Duration, Instant};
use tauri::Manager;

struct Backend(Mutex<Child>);

fn show_startup_error(message: &str) {
    #[cfg(windows)]
    {
        #[link(name = "user32")]
        extern "system" {
            fn MessageBoxW(
                window: *mut std::ffi::c_void,
                text: *const u16,
                caption: *const u16,
                flags: u32,
            ) -> i32;
        }
        let text: Vec<u16> = message.encode_utf16().chain(Some(0)).collect();
        let title: Vec<u16> = "Sparkbot could not start"
            .encode_utf16()
            .chain(Some(0))
            .collect();
        // Both UTF-16 buffers remain alive for the duration of this modal call.
        unsafe {
            MessageBoxW(std::ptr::null_mut(), text.as_ptr(), title.as_ptr(), 0x10);
        }
    }
    #[cfg(not(windows))]
    eprintln!("{message}");
}

fn stop_backend(child: &mut Child) {
    // EOF is the backend's shutdown signal, including if the desktop crashes.
    drop(child.stdin.take());
    let deadline = Instant::now() + Duration::from_secs(5);
    while Instant::now() < deadline {
        if matches!(child.try_wait(), Ok(Some(_))) {
            return;
        }
        std::thread::sleep(Duration::from_millis(100));
    }
    let _ = child.kill();
    let _ = child.wait();
}

#[tauri::command]
fn desktop_connector_command() -> Result<String, String> {
    let path = std::env::current_exe()
        .map_err(|e| e.to_string())?
        .with_file_name("sparkbot-roundtable.exe");
    Ok(format!(
        "& '{}'",
        path.to_string_lossy().replace('\'', "''")
    ))
}

fn main() {
    let app = tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![desktop_connector_command])
        .setup(|app| {
            let binary = std::env::current_exe()?.with_file_name("sparkbot-server.exe");
            let mut command = Command::new(binary);
            command.stdin(Stdio::piped()).stdout(Stdio::piped()).stderr(Stdio::null());
            #[cfg(windows)] {
                use std::os::windows::process::CommandExt;
                command.creation_flags(0x08000000); // CREATE_NO_WINDOW
            }
            let mut child = command.spawn()?;
            let stdout = child.stdout.take().ok_or("Missing backend stdout")?;
            let (tx, rx) = mpsc::channel();
            std::thread::spawn(move || {
                let mut reader = BufReader::new(stdout);
                let mut line = String::new();
                let _ = reader.read_line(&mut line);
                let _ = tx.send(line.trim().to_owned());
                // Drain the pipe for the lifetime of the backend.
                let _ = std::io::copy(&mut reader, &mut std::io::sink());
            });
            if rx.recv_timeout(Duration::from_secs(45)).ok().as_deref() != Some("SPARKBOT_READY") {
                stop_backend(&mut child);
                return Err("Sparkbot could not start its local backend. Close any other Sparkbot Roundtable instance and check that port 18765 is free.".into());
            }
            app.manage(Backend(Mutex::new(child)));
            Ok(())
        })
        .build(tauri::generate_context!());
    let app = match app {
        Ok(app) => app,
        Err(error) => {
            show_startup_error(&error.to_string());
            return;
        }
    };
    app.run(|handle, event| {
        if let tauri::RunEvent::Exit = event {
            if let Some(backend) = handle.try_state::<Backend>() {
                if let Ok(mut child) = backend.0.lock() {
                    stop_backend(&mut child);
                }
            }
        }
    });
}
