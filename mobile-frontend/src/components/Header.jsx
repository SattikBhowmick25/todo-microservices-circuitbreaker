export default function Header({ title, subtitle }) {
  return (
    <div>
      <div className="page-title">{title}</div>
      <div className="page-subtitle">{subtitle}</div>
    </div>
  );
}