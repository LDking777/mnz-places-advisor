import { CATEGORIES } from '../constants/categories'

/**
 * Selector de categoría como grupo de botones pill.
 *
 * @param {string}   value    — categoría actualmente seleccionada.
 * @param {function} onChange — callback al cambiar la selección.
 */
export default function CategoryFilter({ value, onChange }) {
  return (
    <fieldset className="flex flex-wrap gap-2" aria-label="Filtrar por categoría">
      <legend className="sr-only">Categoría turística</legend>
      {CATEGORIES.map((cat) => {
        const isActive = cat.value === value
        return (
          <button
            key={cat.value}
            type="button"
            role="radio"
            aria-checked={isActive}
            onClick={() => onChange(cat.value)}
            className={[
              'inline-flex items-center gap-1.5 rounded-full px-4 py-2 text-sm font-medium',
              'transition-all duration-200 cursor-pointer',
              'border',
              isActive
                ? 'border-emerald-600 bg-emerald-600 text-white shadow-md shadow-emerald-600/20'
                : 'border-coffee-200 bg-white text-coffee-700 hover:border-emerald-400 hover:text-emerald-700 hover:bg-emerald-50',
            ].join(' ')}
          >
            <span aria-hidden="true">{cat.icon}</span>
            {cat.label}
          </button>
        )
      })}
    </fieldset>
  )
}
