import React from 'react';
import { Link } from 'react-router-dom';

export const MetricCard = ({ title, value, subtext, icon: Icon, badgeColor = 'blue', linkTo }) => {
  const badgeStyles = {
    blue: 'bg-blue-50 text-blue-600 border-blue-200',
    green: 'bg-emerald-50 text-emerald-600 border-emerald-200',
    amber: 'bg-amber-50 text-amber-600 border-amber-200',
    purple: 'bg-purple-50 text-purple-600 border-purple-200',
    teal: 'bg-teal-50 text-teal-600 border-teal-200',
  };

  const iconContainerStyles = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-emerald-50 text-emerald-600',
    amber: 'bg-amber-50 text-amber-600',
    purple: 'bg-purple-50 text-purple-600',
    teal: 'bg-teal-50 text-teal-600',
  };

  const CardContent = (
    <div className="flex items-start justify-between p-5 bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
      <div>
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
          {title}
        </span>
        <span className="text-3xl font-extrabold text-slate-900 tracking-tight block">
          {value !== undefined && value !== null ? value : 0}
        </span>
        {subtext && (
          <span className="inline-block mt-2 text-xs font-medium text-slate-500">
            {subtext}
          </span>
        )}
      </div>
      {Icon && (
        <div className={`p-3 rounded-full ${iconContainerStyles[badgeColor] || iconContainerStyles.blue} shrink-0`}>
          <Icon className="w-6 h-6" />
        </div>
      )}
    </div>
  );

  if (linkTo) {
    return <Link to={linkTo} className="block">{CardContent}</Link>;
  }

  return CardContent;
};

export default MetricCard;
