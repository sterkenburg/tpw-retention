import { getLatestStats } from "@/lib/bigquery";
import { OverviewClient } from "./OverviewClient";

export const dynamic = "force-dynamic";

export default async function OverviewPage() {
  const suppliers = await getLatestStats();
  return <OverviewClient suppliers={suppliers} />;
}
