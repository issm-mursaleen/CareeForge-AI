"use client";
import { ButtonHTMLAttributes, forwardRef } from "react";
import { cn } from "@/lib/utils";

type Variant = "primary" | "ghost" | "outline";
type Size = "sm" | "md" | "lg";

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
}

const variants: Record<Variant, string> = {
  primary: "bg-primary text-on-primary hover:opacity-90 shadow-sm",
  ghost: "bg-surface-container text-on-surface hover:bg-surface-container-high",
  outline: "border border-outline-variant text-on-surface hover:bg-surface-container",
};

const sizes: Record<Size, string> = {
  sm: "h-9 px-3 text-label-md font-label-md",
  md: "h-11 px-5 text-label-md font-label-md",
  lg: "h-12 px-6 text-body-md font-body-md font-bold",
};

export const Button = forwardRef<HTMLButtonElement, Props>(
  ({ variant = "primary", size = "md", loading, className, children, disabled, ...rest }, ref) => (
    <button
      ref={ref}
      disabled={disabled || loading}
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed",
        variants[variant],
        sizes[size],
        className,
      )}
      {...rest}
    >
      {loading && (
        <span className="h-4 w-4 animate-spin rounded-full border-2 border-on-primary/30 border-t-on-primary" />
      )}
      {children}
    </button>
  ),
);
Button.displayName = "Button";
