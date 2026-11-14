# the-music-tree-api-kit

[![Test](https://github.com/BehindTheMusicTree/the-music-tree-api-kit/actions/workflows/test.yml/badge.svg)](https://github.com/BehindTheMusicTree/the-music-tree-api-kit/actions/workflows/test.yml)

Shared generic HTTP-layer Django library (error handling, pagination, filtering, viewsets) for `hear-the-music-tree-api` and `grow-the-music-tree-api`. Installable Python package — not a deployable service. No genre/tag/criteria/tree coupling; that lives in `the-music-tree-genre-kit`, which depends on this package.

`AppModelViewSet.get_object()` resolves details through `get_detail_queryset()`
(defaulting to `get_queryset()`), enforces private ownership, and checks object
permissions once. Keep visibility restrictions in `get_queryset()`. Collection
filter backends do not run for detail lookups; override `get_detail_queryset()`
when a resource explicitly requires additional detail filtering.
