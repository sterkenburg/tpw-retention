import { getLatestStats } from "@/lib/bigquery";
import { SupplierTable } from "@/components/SupplierTable";
import { StatCard } from "@/components/StatCard";

export const dynamic = "force-dynamic";

export default async function ActionsPage() {
  const suppliers = await getLatestStats();

  const p1 = suppliers.filter((s) => s.priority_tier === "P1");
  const renewalSoon = suppliers.filter(
    (s) => s.days_until_renewal != null && s.days_until_renewal < 60
  );
  const noLeads = suppliers.filter((s) => s.days_since_last_lead > 45);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Action Queue</h1>
        <p className="text-sm text-gray-500 mt-1">
          What needs attention today.
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <StatCard
          label="P1 — Urgent Calls"
          value={p1.length}
          subtext="Call within 24h"
          color="red"
        />
        <StatCard
          label="Renewal < 60d"
          value={renewalSoon.length}
          subtext="Prepare renewal outreach"
          color="orange"
        />
        <StatCard
          label="No Leads 45d+"
          value={noLeads.length}
          subtext="Re-engagement needed"
          color="blue"
        />
      </div>

      <div className="space-y-6">
        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-3">
            P1 — Urgent ({p1.length})
          </h2>
          <SupplierTable suppliers={p1} />
        </section>

        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-3">
            Renewals Approaching ({renewalSoon.length})
          </h2>
          <SupplierTable suppliers={renewalSoon} />
        </section>

        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-3">
            No Leads in 45+ Days ({noLeads.length})
          </h2>
          <SupplierTable suppliers={noLeads} />
        </section>
      </div>
    </div>
  );
}
