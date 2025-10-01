import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Star } from "lucide-react";

interface PositiveTipCardProps {
  tip: string;
}

export const PositiveTipCard: React.FC<PositiveTipCardProps> = ({ tip }) => {
  return (
    <div className="w-fit mx-auto">
      <div className="py-4 px-6">
        <div className="flex items-center gap-3 whitespace-nowrap">
            <p className="text-xl font-bold text-foreground">{tip}</p>
        </div>
      </div>
    </div>
  );
};
