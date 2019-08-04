- FAB changes:
  - get REST endpoint must return edit_columns also so we can render a form with values on the client
  - filters are missing labels and types
  - get methods should return page and page_size
  - Better error handling on filters, ex: invalid operations on column
  - select look into react-select-async-paginate and evaluate change select values to {value, label} from {id, value}
  