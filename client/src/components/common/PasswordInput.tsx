import { Eye, EyeOff } from "lucide-react";
import { useState } from "react";
import { Input } from "../ui/input";

export function PasswordInput({ field, placeholder }: { field: any; placeholder: string }) {
  const [visible, setVisible] = useState(false);

  return (
    <div className="relative">
      <Input type={visible ? "text" : "password"} placeholder={placeholder} {...field} />
      <button
        type="button"
        className="absolute inset-y-0 right-3 flex items-center"
        onClick={() => setVisible((prev) => !prev)}
      >
        {visible ? <EyeOff size={18} /> : <Eye size={18} />}
      </button>
    </div>
  );
}
