import { ReactNode } from 'react'
import { classNames } from '@utils/helpers'

export type BadgeVariant = 'default' | 'primary' | 'success' | 'danger' | 'warning' | 'info'
export type BadgeSize = 'sm' | 'md' | 'lg'

interface BadgeProps {
  children: ReactNode
  variant?: BadgeVariant
  size?: BadgeSize
  dot?: boolean
  className?: string
}

const variantClasses: Record<BadgeVariant, string> = {
  default: 'bg-gray-100 text-gray-800',
  primary: 'bg-primary-100 text-primary-800',
  success: 'bg-green-100 text-green-800',
  danger: 'bg-red-100 text-red-800',
  warning: 'bg-yellow-100 text-yellow-800',
  info: 'bg-blue-100 text-blue-800',
}

const sizeClasses: Record<BadgeSize, string> = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-sm',
  lg: 'px-3 py-1.5 text-base',
}

const dotClasses: Record<BadgeVariant, string> = {
  default: 'bg-gray-400',
  primary: 'bg-primary-600',
  success: 'bg-green-600',
  danger: 'bg-red-600',
  warning: 'bg-yellow-600',
  info: 'bg-blue-600',
}

export default function Badge({
  children,
  variant = 'default',
  size = 'md',
  dot = false,
  className,
}: BadgeProps) {
  return (
    <span
      className={classNames(
        'inline-flex items-center gap-1.5 font-medium rounded-full',
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
    >
      {dot && (
        <span
          className={classNames(
            'w-1.5 h-1.5 rounded-full',
            dotClasses[variant]
          )}
        />
      )}
      {children}
    </span>
  )
}
