import type { Metadata } from "next";
import { WorkflowsTable } from "@/components/dashboard/workflows-table";
import { MobileRedirectWrapper } from "@/components/dashboard/mobile-redirect-wrapper";

export const metadata: Metadata = {
  title: "Dashboard | AutoML Platform",
  description:
    "Your AutoML Platform dashboard. Access your datasets, train machine learning models, and explore learning resources.",
};

export default function DashboardPage() {
  return (
    <MobileRedirectWrapper>
      <div className="flex flex-col gap-6 p-6">
        <div>
          <h1 className="text-2xl font-semibold text-foreground mb-1">
            My Workflows
          </h1>
          <p className="text-muted-foreground">
            View and manage your machine learning workflow executions
          </p>
        </div>

        <WorkflowsTable />
      </div>
    </MobileRedirectWrapper>
  );
}
