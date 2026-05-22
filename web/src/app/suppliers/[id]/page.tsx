import Link from "next/link";
import {
  getSupplierById,
  getActionsForSupplier,
  getInterventionsForSupplier,
} from "@/lib/bigquery";
import { TierBadge } from "@/components/TierBadge";
import { ActionHistory } from "@/components/ActionHistory";
import { notFound } from "next/navigation";

export const dynamic = "force-dynamic";

export default async function SupplierPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const supplier = await getSupplierById(id);

  if (!supplier) {
    notFound();
  }

  const [actions, interventions] = await Promise.all([
    getActionsForSupplier(id),
    getInterventionsForSupplier(id),
  ]);

  const riskPercent = Math.round(supplier.churn_probability * 100);

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-gray-500">
        <Link href="/" className="hover:text-gray-900">
          Overview
        </Link>
        <span>/</span>
        <span className="text-gray-900 font-medium">
          {supplier.profile_name}
        </span>
      </div>

      {/* Header Card */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-gray-900">
                {supplier.profile_name}
              </h1>
              <TierBadge tier={supplier.priority_tier} />
              {supplier.already_renewed && (
                <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full font-medium">
                  Already renewed
                </span>
              )}
            </div>
            <p className="text-sm text-gray-500 mt-1">
              {supplier.category} · {supplier.account_manager ?? "No AM"}
            </p>
          </div>
          <a
            href={`https://admin.theperfectwedding.nl/profiles/edit/${supplier.profile_id}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            Open in Admin →
          </a>
        </div>
      </div>

      {/* Health Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <p className="text-xs font-medium text-gray-500">Plan Value</p>
          <p className="mt-1 text-xl font-bold text-gray-900">
            €{supplier.plan_value?.toLocaleString("nl-NL") ?? 0}
          </p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <p className="text-xs font-medium text-gray-500">Renewal</p>
          <p
            className={`mt-1 text-xl font-bold ${
              supplier.days_until_renewal < 30
                ? "text-red-600"
                : "text-gray-900"
            }`}
          >
            {supplier.days_until_renewal != null
              ? `${supplier.days_until_renewal} days`
              : "—"}
          </p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <p className="text-xs font-medium text-gray-500">Profile Views (60d)</p>
          <p className="mt-1 text-xl font-bold text-gray-900">
            {supplier.profile_views_60d}
          </p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <p className="text-xs font-medium text-gray-500">Leads (60d)</p>
          <p className="mt-1 text-xl font-bold text-gray-900">
            {supplier.leads_60d}
          </p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <p className="text-xs font-medium text-gray-500">Profile Views (contract)</p>
          <p className="mt-1 text-xl font-bold text-gray-900">
            {supplier.contract_views_total}
          </p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <p className="text-xs font-medium text-gray-500">Leads (contract)</p>
          <p className="mt-1 text-xl font-bold text-gray-900">
            {supplier.contract_leads_total}
          </p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <p className="text-xs font-medium text-gray-500">Category Avg Views (60d)</p>
          <p className="mt-1 text-xl font-bold text-gray-900">
            {supplier.category_avg_views_60d?.toFixed(0) ?? "—"}
          </p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <p className="text-xs font-medium text-gray-500">Category Avg Leads (60d)</p>
          <p className="mt-1 text-xl font-bold text-gray-900">
            {supplier.category_avg_leads_60d?.toFixed(1) ?? "—"}
          </p>
        </div>
      </div>

      {/* Risk + Signals */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-sm font-semibold text-gray-900 mb-4">
            Churn Risk
          </h2>
          <div className="flex items-center gap-4">
            <div className="relative w-24 h-24">
              <svg className="w-full h-full" viewBox="0 0 36 36">
                <path
                  className="text-gray-100"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="3"
                />
                <path
                  className={
                    riskPercent >= 80
                      ? "text-red-500"
                      : riskPercent >= 55
                      ? "text-orange-500"
                      : riskPercent >= 35
                      ? "text-yellow-500"
                      : "text-green-500"
                  }
                  strokeDasharray={`${riskPercent}, 100`}
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="3"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-lg font-bold text-gray-900">
                  {riskPercent}%
                </span>
              </div>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">
                {supplier.priority_tier} —{" "}
                {supplier.risk_factors !== "Stable"
                  ? supplier.risk_factors
                  : "No major risk factors"}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {supplier.recommended_action}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-sm font-semibold text-gray-900 mb-4">
            Activity Signals
          </h2>
          <div className="space-y-3">
            <SignalRow
              label="Days since last login"
              value={supplier.days_since_last_login}
              warning={supplier.days_since_last_login > 30}
            />
            <SignalRow
              label="Days since last lead"
              value={supplier.days_since_last_lead}
              warning={supplier.days_since_last_lead > 60}
            />
            <SignalRow
              label="Engagement trend"
              value={`${(supplier.engagement_trend * 100).toFixed(0)}%`}
              warning={supplier.engagement_trend < -0.5}
            />
          </div>
        </div>
      </div>

      {/* Action History */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-sm font-semibold text-gray-900 mb-4">
          Action History
        </h2>
        <ActionHistory actions={actions} interventions={interventions} />
      </div>
    </div>
  );
}

function SignalRow({
  label,
  value,
  warning,
}: {
  label: string;
  value: string | number;
  warning: boolean;
}) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-gray-600">{label}</span>
      <span
        className={`text-sm font-medium ${
          warning ? "text-red-600" : "text-gray-900"
        }`}
      >
        {value}
      </span>
    </div>
  );
}
