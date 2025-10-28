import Link from "next/link";
import {
  Sidebar,
  SidebarContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "../ui/sidebar";
import { User2, Settings, Webcam } from "lucide-react";

const items = [
  { title: "Cabinet", url: "#", icon: User2 },
  { title: "Make Call", url: "#", icon: Webcam },
  { title: "Settings", url: "#", icon: Settings },
];

export default function DashboardSidebar() {
  return (
    <Sidebar>
      <SidebarContent>
        <SidebarMenu>
          {items.map((item) => (
            <SidebarMenuItem key={item.title}>
              <SidebarMenuButton>
                <Link href={item.url} className="flex justify-between">
                  <item.icon />
                  <span>{item.title}</span>
                </Link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          ))}
        </SidebarMenu>
      </SidebarContent>
    </Sidebar>
  );
}
