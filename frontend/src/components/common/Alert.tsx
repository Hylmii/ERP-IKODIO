import { ReactNode } from 'react'
import { FiAlertCircle, FiAlertTriangle, FiCheckCircle, FiInfo } from 'react-icons/fi'
import { classNames } from '@utils/helpers'

export type AlertVariant = 'info' | 'success' | 'warning' | 'danger'

interface AlertProps {
  variant?: AlertVariant
  title?: string
  children: ReactNode
  className?: string
  onClose?: () => void
}

const variantConfig: Record<
  AlertVariant,
  { bgClass: string; borderClass: string; textClass: string; icon: ReactNode }
> = {
  info: {
    bgClass: 'bg-blue-50',
    borderClass: 'border-blue-200',
    textClass: 'text-blue-800',
    icon: <FiInfo className="w-5 h-5 text-blue-600" />,
  },
  success: {
    bgClass: 'bg-green-50',
    borderClass: 'border-green-200',
    textClass: 'text-green-800',
    icon: <FiCheckCircle className="w-5 h-5 text-green-600" />,
  },
  warning: {
    bgClass: 'bg-yellow-50',
    borderClass: 'border-yellow-200',
    textClass: 'text-yellow-800',
    icon: <FiAlertTriangle className="w-5 h-5 text-yellow-600" />,
  },
  danger: {
    bgClass: 'bg-red-50',
    borderClass: 'border-red-200',
    textClass: 'text-red-800',
    icon: <FiAlertCircle className="w-5 h-5 text-red-600" />,
  },
}

export default function Alert({
  variant = 'info',
  title,
  children,
  className,
  onClose,
}: AlertProps) {
  const config = variantConfig[variant]

  return (
    <div
      className={classNames(
        'rounded-lg border p-4',
        config.bgClass,
        config.borderClass,
        className
      )}
    >
      <div className="flex gap-3">
        <div className="flex-shrink-0">{config.icon}</div>
        <div className="flex-1">
          {title && (
            <h4 className={classNames('font-semibold mb-1', config.textClass)}>
              {title}
            </h4>
          )}
          <div className={classNames('text-sm', config.textClass)}>
            {children}
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className={classNames(
              'flex-shrink-0 ml-auto text-sm font-medium hover:underline',
              config.textClass
            )}
          >
            Dismiss
          </button>
        )}
      </div>
    </div>
  )
}
