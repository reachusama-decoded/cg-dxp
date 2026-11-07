# TypeScript Coding Standards

## Governing Authority

These standards are derived from and comply with:

- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/)
- [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- [React Documentation](https://react.dev/)
- [MDN Web Docs](https://developer.mozilla.org/en-US/)
- [typescript-eslint Documentation](https://typescript-eslint.io/)
- [Prettier Documentation](https://prettier.io/docs/)
- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library Documentation](https://testing-library.com/docs/react-testing-library/intro/)

Where this document is silent, the Airbnb JavaScript Style Guide applies.

## Rule Format

Same shape as the rest of RFD 0008:

```
### TS-{CATEGORY}-{NNN} — one-line directive

**Severity:** error | warning | advisory
**Since:** v0.1.0
**Linter:** ESLint / typescript-eslint / tsc / Prettier / advisory

**Decision.** What to do.
**Why.** Rationale.
**Exception.** When the rule does not apply, or "None."
**Examples.** good / bad code.
```

Categories: `VERSION`, `IMPORT`, `NAMING`, `TYPE`, `REACT`, `IDIOM`, `ASYNC`,
`ERROR`, `TEST`, `SECURITY`.

## Tooling

### Formatter: Prettier

```json
// .prettierrc
{
  "semi": true,
  "singleQuote": true,
  "trailingComma": "all",
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "bracketSpacing": true,
  "arrowParens": "always",
  "endOfLine": "lf"
}
```

### Linter: ESLint + typescript-eslint (strict-type-checked)

```js
// eslint.config.mjs
import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  eslint.configs.recommended,
  ...tseslint.configs.strictTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,
  {
    rules: {
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/no-unsafe-assignment': 'error',
      '@typescript-eslint/no-unsafe-call': 'error',
      '@typescript-eslint/no-unsafe-member-access': 'error',
      '@typescript-eslint/no-unsafe-return': 'error',
      '@typescript-eslint/no-unsafe-argument': 'error',
      '@typescript-eslint/no-non-null-assertion': 'error',
      '@typescript-eslint/strict-boolean-expressions': 'error',
      '@typescript-eslint/switch-exhaustiveness-check': 'error',
      '@typescript-eslint/consistent-type-imports': [
        'error',
        { prefer: 'type-imports', fixStyle: 'inline-type-imports' },
      ],
      '@typescript-eslint/no-unnecessary-condition': 'error',
      '@typescript-eslint/prefer-nullish-coalescing': 'error',
      '@typescript-eslint/no-floating-promises': 'error',
      '@typescript-eslint/no-misused-promises': 'error',
      '@typescript-eslint/require-await': 'error',
      'react/jsx-no-target-blank': 'error',
      'react-hooks/rules-of-hooks': 'error',
      'react-hooks/exhaustive-deps': 'error',
      'jsx-a11y/alt-text': 'error',
      'jsx-a11y/anchor-is-valid': 'error',
    },
  },
);
```

### TypeScript Compiler: Strict Mode

```jsonc
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "forceConsistentCasingInFileNames": true,
    "exactOptionalPropertyTypes": true,
    "noPropertyAccessFromIndexSignature": true,

    "module": "ESNext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "verbatimModuleSyntax": true,

    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "jsx": "react-jsx",
    "declaration": true,
    "sourceMap": true,
    "skipLibCheck": true
  }
}
```

---

## Rule index

Rules are split by category. Each category file has the rules in numeric order.

- [`async.md`](async.md) — **Async** (3 rules). async/await, floating promises, parallel patterns.
- [`error.md`](error.md) — **Error Handling** (4 rules). catch unknowns, domain error classes, error chaining.
- [`idiom.md`](idiom.md) — **Idioms** (5 rules). Boolean expressions, ternaries, useReducer, zod validation.
- [`import.md`](import.md) — **Imports** (3 rules). Import grouping and named-export policy.
- [`naming.md`](naming.md) — **Naming** (7 rules). Identifier casing and file naming conventions.
- [`react.md`](react.md) — **React** (12 rules). Functional components, hooks, server state, rendering rules.
- [`security.md`](security.md) — **Security** (6 rules). XSS, dynamic code, auth tokens, input validation, URL encoding.
- [`test.md`](test.md) — **Testing** (7 rules). Vitest, React Testing Library, MSW, snapshot policy.
- [`type.md`](type.md) — **Types** (8 rules). Strict type safety: any, non-null, narrowing, satisfies, discriminated unions.
- [`version.md`](version.md) — **Version** (5 rules). TypeScript, ECMAScript, React, and Node.js versions.
