import { Button } from "@/components/ui/button";
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { LogIn, UserPlus2 } from "lucide-react";
import Link from "next/link";

export default function Home() {
  return (
    <main className="w-screen h-screen flex justify-center items-center">
      <Card className="w-1/4 h-1/3 flex justify-between">
        <CardHeader>
          <CardTitle className="text-3xl">
            Добро пожаловать в VideoChatApp!
          </CardTitle>
          <CardDescription className="text-md">
            Общайтесь с друзьями и коллегами в HD-видеозвонках. Присоединяйтесь
            к комнате или создайте новую за секунды.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <CardAction>
            <Link href={"/login"}>
              <Button className="mr-1">
                <LogIn />
                <span>Войти</span>
              </Button>
            </Link>
            <Link href={"/signup"}>
              <Button variant={"outline"}>
                <UserPlus2 />
                <span>Зарегистрироваться</span>
              </Button>
            </Link>
          </CardAction>
        </CardContent>
      </Card>
    </main>
  );
}
