type RoadmapCardProps = {
  title: string;
  items: string[];
};

export default function RoadmapCard({ title, items }: RoadmapCardProps) {
  return (
    <article className="roadmap-card">
      <h3>{title}</h3>
      <ul>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </article>
  );
}
