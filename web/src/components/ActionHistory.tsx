"use client";

import { ActionLog, InterventionLog } from "@/lib/bigquery";

function formatDate(d: string) {
  return new Date(d).toLocaleDateString("nl-NL", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export function ActionHistory({
  actions,
  interventions,
}: {
  actions: ActionLog[];
  interventions: InterventionLog[];
}) {
  const allEvents = [
    ...actions.map((a) => ({
      type: "action" as const,
      date: a.action_date,
      title: a.action_type,
      detail: a.action_detail,
      status: a.executed ? "Done" : "Pending",
    })),
    ...interventions.map((i) => ({
      type: "intervention" as const,
      date: i.created_at,
      title: i.intervention_type,
      detail: i.recommended_action,
      status: `Assigned to ${i.assigned_to || "—"}`,
    })),
  ].sort(
    (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
  );

  if (allEvents.length === 0) {
    return (
      <p className="text-sm text-gray-500 py-4">
        No actions or interventions recorded yet.
      </p>
    );
  }

  return (
    <div className="flow-root">
      <ul className="-mb-8">
        {allEvents.map((event, idx) => (
          <li key={idx}>
            <div className="relative pb-8">
              {idx !== allEvents.length - 1 && (
                <span
                  className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                  aria-hidden="true"
                />
              )}
              <div className="relative flex space-x-3">
                <div
                  className={`h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white ${
                    event.type === "action"
                      ? "bg-blue-500"
                      : "bg-purple-500"
                  }`}
                >
                  {event.type === "action" ? (
                    <svg
                      className="h-4 w-4 text-white"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M13 10V3L4 14h7v7l9-11h-7z"
                      />
                    </svg>
                  ) : (
                    <svg
                      className="h-4 w-4 text-white"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm">
                    <span className="font-medium text-gray-900">
                      {event.title}
                    </span>
                    <span className="ml-2 text-xs text-gray-500">
                      {formatDate(event.date)}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">{event.detail}</p>
                  <p className="text-xs text-gray-400 mt-0.5">
                    {event.status}
                  </p>
                </div>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
