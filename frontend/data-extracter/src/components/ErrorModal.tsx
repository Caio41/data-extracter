import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function ErrorModal({ message, onClose }: { message: string, onClose: () => void }) {
  return (
    <div className="fixed inset-0 flex items-center justify-center z-50" style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)' }}>
      <Card className="w-full max-w-lg p-6 shadow-lg bg-white">
        <CardContent>
          <h2 className="text-lg font-semibold text-center text-red-500">Erro</h2>
          <p className="text-center mt-2">{message}</p>
          <div className="flex justify-center mt-4">
            <Button onClick={onClose}>Fechar</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
