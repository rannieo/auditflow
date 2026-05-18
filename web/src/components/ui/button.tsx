import * as React from 'react'
import { Slot } from '@radix-ui/react-slot'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default:
          'bg-[#1e3a5f] text-white hover:bg-[#172f4d] focus-visible:ring-[#1e3a5f]',
        secondary:
          'bg-white text-slate-900 border border-slate-200 hover:bg-slate-50 focus-visible:ring-slate-400',
        ghost:
          'text-slate-700 hover:bg-slate-100 focus-visible:ring-slate-300',
        accent:
          'bg-[#059669] text-white hover:bg-[#047857] focus-visible:ring-[#059669]',
        destructive:
          'bg-[#dc2626] text-white hover:bg-[#b91c1c] focus-visible:ring-[#dc2626]',
      },
      size: {
        default: 'h-9 px-4',
        sm: 'h-8 px-3 text-xs',
        lg: 'h-10 px-6',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button'
    return (
      <Comp
        ref={ref}
        className={cn(buttonVariants({ variant, size, className }))}
        {...props}
      />
    )
  },
)
Button.displayName = 'Button'
