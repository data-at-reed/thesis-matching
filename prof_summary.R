library(tidyverse)

data <- read_csv("~/Documents/ThesisAssignments/2024/matched.csv")


summary <- data %>% 
  group_by(`Matched Advisor`, Major) %>%
  dplyr::summarize(n = n_distinct(ID)) %>%
  pivot_wider(names_from = Major,
              values_from = n, 
              values_fill = 0) %>%
  mutate(Total = rowSums(across(where(is.numeric))))

write_csv(summary, "~/Documents/ThesisAssignments/2024/matched_summary.csv")


