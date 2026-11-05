
interface StatusCardProps {
  titulo: string;
  estado: string;
  descripcion: string;
}

function StatusCard({
  titulo,
  estado,
  descripcion
}: StatusCardProps) {
  return (
    <section className="status-card">
      <h2>{titulo}</h2>
      <p>Estado: {estado}</p>
      <p>{descripcion}</p>
    </section>
  );
}

export default StatusCard;
