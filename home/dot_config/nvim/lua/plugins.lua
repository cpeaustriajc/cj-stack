-- Neovim 0.12's built-in package manager is available as vim.pack.

if vim.pack == nil then
  vim.notify("vim.pack is unavailable; this config expects Neovim 0.12+", vim.log.levels.WARN)
  return
end

-- Add telescope and its dependencies
vim.pack.add({
  "https://github.com/nvim-lua/plenary.nvim",
  "https://github.com/nvim-telescope/telescope.nvim",
})

-- Setup telescope with sensible defaults
require("telescope").setup({
  defaults = {
    file_ignore_patterns = { "node_modules", ".git/", ".cache/" },
    sorting_strategy = "ascending",
    layout_config = {
      prompt_position = "top",
    },
  },
  pickers = {
    find_files = {
      hidden = true,
    },
  },
})
