"use client";

export function StatCard({
  label,
  value,
  subtext,
  color = "blue",
}: {
  label: string;
  value: string | number;
  subtext?: string;
  color?: "blue" | "red" | "orange" | "green";
}) {
  const colorClasses = {
    blue: "bg-blue-50 border-blue-100",
    red: "bg-red-50 border-red-100",
    orange: "bg-orange-50 border-orange-100",
    green: "bg-green-50 border-green-100",
  };

  return (
    <div className={`rounded-xl border p-5 ${colorClasses[color]}`}>
      <p className="text-sm font-medium text-gray-600">{label}</p>
      <p className="mt-1 text-2xl font-bold text-gray-900">{value}</p>
      {subtext && <p className="mt-1 text-xs text-gray-500">{subtext}</p>}
    </div>
  );
}
