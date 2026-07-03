import { useId } from "react";
import type { ComponentProps, ReactNode } from "react";

import { Check, ChevronDown } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

type DonorFieldProps = {
  label: ReactNode;
  hint?: ReactNode;
  children: ReactNode;
  className?: string;
};

type DonorSelectOption = {
  value: string;
  label: ReactNode;
  description?: ReactNode;
};

export function DonorField({ label, hint, children, className }: DonorFieldProps) {
  return (
    <label className={cn("grid min-w-0 gap-2 text-sm font-medium text-slate-100", className)}>
      <span className="text-sm font-semibold text-slate-100">{label}</span>
      {children}
      {hint ? <span className="text-xs font-normal leading-5 text-slate-400">{hint}</span> : null}
    </label>
  );
}

export function DonorFieldGrid({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return <div className={cn("grid min-w-0 gap-4 md:grid-cols-2", className)}>{children}</div>;
}

export function DonorTextInput({
  className,
  ...props
}: ComponentProps<typeof Input>) {
  return (
    <Input
      className={cn(
        "h-11 rounded-2xl border border-white/10 bg-slate-950/65 px-4 text-sm text-slate-100 shadow-inner shadow-black/20 placeholder:text-slate-500 focus-visible:border-cyan-300/30 focus-visible:ring-cyan-300/40 disabled:border-white/5 disabled:bg-slate-900/40 disabled:text-slate-500",
        className,
      )}
      {...props}
    />
  );
}

export function DonorTextarea({
  className,
  ...props
}: ComponentProps<typeof Textarea>) {
  return (
    <Textarea
      className={cn(
        "min-h-[112px] rounded-2xl border border-white/10 bg-slate-950/65 px-4 py-3 text-sm text-slate-100 shadow-inner shadow-black/20 placeholder:text-slate-500 focus-visible:border-cyan-300/30 focus-visible:ring-cyan-300/40 disabled:border-white/5 disabled:bg-slate-900/40 disabled:text-slate-500",
        className,
      )}
      {...props}
    />
  );
}

export function DonorChip({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex max-w-full items-center rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs font-semibold leading-5 text-slate-200",
        className,
      )}
    >
      {children}
    </span>
  );
}

export function DonorSelect({
  label,
  value,
  options,
  placeholder = "Selecionar",
  onChange,
  className,
}: {
  label: ReactNode;
  value: string;
  options: DonorSelectOption[];
  placeholder?: ReactNode;
  onChange: (value: string) => void;
  className?: string;
}) {
  const labelId = useId();
  const valueId = useId();
  const selected = options.find((option) => option.value === value);
  const displayLabel = selected?.label ?? placeholder;

  return (
    <div className={cn("grid min-w-0 gap-2", className)}>
      <span id={labelId} className="text-sm font-semibold text-slate-100">{label}</span>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            type="button"
            variant="outline"
            className="h-11 w-full min-w-0 justify-between rounded-2xl border-white/10 bg-slate-950/65 px-4 text-left text-sm text-slate-100 shadow-inner shadow-black/20 hover:border-cyan-300/30 hover:bg-slate-900/80 focus-visible:ring-cyan-300/40"
            aria-labelledby={`${labelId} ${valueId}`}
          >
            <span id={valueId} className="min-w-0 truncate text-left">{displayLabel}</span>
            <ChevronDown className="h-4 w-4 shrink-0 text-slate-300" aria-hidden="true" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent
          align="start"
          sideOffset={6}
          className="z-50 max-h-80 w-[var(--radix-dropdown-menu-trigger-width)] min-w-64 overflow-auto rounded-2xl border border-white/10 bg-slate-950/95 p-2 text-slate-100 shadow-[0_24px_80px_-24px_rgba(0,0,0,0.95)] backdrop-blur-xl"
        >
          {options.map((option) => {
            const isSelected = option.value === value;
            return (
              <DropdownMenuItem
                key={option.value}
                className="grid cursor-pointer gap-1 rounded-xl px-3 py-2.5 text-left text-slate-100 outline-none transition-colors focus:bg-cyan-400/10 focus:text-slate-50 data-[highlighted]:bg-cyan-400/10 data-[highlighted]:text-slate-50"
                onSelect={(event) => {
                  event.preventDefault();
                  onChange(option.value);
                }}
              >
                <span className="flex min-w-0 flex-1 items-start gap-3">
                  <span className="min-w-0 flex-1 break-words text-left text-sm leading-5">{option.label}</span>
                  {isSelected ? <Check className="mt-0.5 h-4 w-4 shrink-0 text-cyan-200" aria-hidden="true" /> : null}
                </span>
                {option.description ? (
                  <span className="mt-1 block text-left text-xs leading-5 text-slate-400">
                    {option.description}
                  </span>
                ) : null}
              </DropdownMenuItem>
            );
          })}
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
