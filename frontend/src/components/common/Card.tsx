import { ReactNode } from 'react'
import { classNames } from '@utils/helpers'

interface CardProps {
  children: ReactNode
  title?: string
  subtitle?: string
  headerAction?: ReactNode
  footer?: ReactNode
  className?: string
  padding?: 'none' | 'sm' | 'md' | 'lg'
  hoverable?: boolean
  onClick?: () => void
}

const paddingClasses = {
  none: '',
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
}

export default function Card({
  children,
  title,
  subtitle,
  headerAction,
  footer,
  className,
  padding = 'md',
  hoverable = false,
  onClick,
}: CardProps) {
  return (
    <div
      className={classNames(
        'bg-white rounded-xl border border-gray-200 shadow-sm',
        hoverable && 'hover:shadow-md transition-shadow duration-200',
        onClick && 'cursor-pointer',
        className
      )}
      onClick={onClick}
    >
      {/* Header */}
      {(title || subtitle || headerAction) && (
        <div className={classNames('border-b border-gray-200', paddingClasses[padding])}>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              {title && (
                <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
              )}
              {subtitle && (
                <p className="mt-1 text-sm text-gray-600">{subtitle}</p>
              )}
            </div>
            {headerAction && <div className="ml-4">{headerAction}</div>}
          </div>
        </div>
      )}

      {/* Body */}
      <div className={paddingClasses[padding]}>{children}</div>

      {/* Footer */}
      {footer && (
        <div className={classNames('border-t border-gray-200 bg-gray-50 rounded-b-xl', paddingClasses[padding])}>
          {footer}
        </div>
      )}
    </div>
  )
}
