import DashboardSidebar from "@/components/dashboard/d-sidebar";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { ReactNode } from "react";

export default function DashboardLayout({
  children,
}: Readonly<{ children: ReactNode }>) {
  return (
    <SidebarProvider>
      <DashboardSidebar />
      <section>
        <SidebarTrigger></SidebarTrigger>
        {children}
      </section>
    </SidebarProvider>
  );
}
