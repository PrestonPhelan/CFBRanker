get.modeling.data <- function() {
  raw_data = read.csv('composite_sagarin.csv')
  selected_data = raw_data[c("Sagarin", "Composite")]
  colnames(selected_data) <- c("rating", "composite")
  selected_data
}

build.model <- function() {
  modeling_data <- get.modeling.data()
  composite = modeling_data$composite
  fit <- lm(modeling_data$rating ~ poly(composite, 8, raw=TRUE))
  fit
}

get.power.data <- function() {
  sourcefile = 'CFBRanker/output/power-ratings-week14.csv'
  print('Reading data from...')
  print(sourcefile)
  power_data = read.csv(sourcefile, header=FALSE)
  colnames(power_data) <- c("composite", "median", "stdev", "rank", "team")
  power_data
}

get.combined.data <- function() {
  sourcefile = 'CFBRanker/output/results-week14.csv'
  print('Reading data from...')
  print(sourcefile)
  combined_data = read.csv(sourcefile, header=FALSE)
  colnames(combined_data) <- c("rank", "power", "performance", "composite", "rating", "team")
  combined_data
}

get.ratings <- function(composite_data, model) {
  ratings = predict(model, data.frame(composite=composite_data$composite))
  data.frame(team=composite_data$team, ratings=ratings)
}

build.ratings.from.power <- function(model) {
  ratings <- get.ratings(get.power.data(), model)
  write.csv(ratings, 'CFBRanker/output/ratings-from-power.csv')
}

build.ratings.from.combined <- function(model) {
  ratings <- get.ratings(get.combined.data(), model)
  write.csv(ratings, 'CFBRanker/output/ratings-from-combined.csv')
}
