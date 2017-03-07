# Atte Keltanen
# atke@cs.helsinki.fi
# 2017/03/03
# Data wrangling of beer data for multiple correspondence analysis

library(dplyr)

beers <- read.csv("beers.csv", sep=";", header=T, quote="\"", row.names = NULL)

# remove duplicated beers because there are many same names for some reason
beers <- beers[!duplicated(beers$X), ]

# tweak some columns to be in desired formats
beers$score <- as.numeric(as.character(beers$score))
beers$score_style <- as.numeric(as.character(beers$score_style))
beers$abv <- as.numeric(as.character(beers$abv))
beers$retired <- as.factor(as.character(beers$retired))

# remove beers with missing values
beers <- beers[!is.na(beers$score), ]
beers <- beers[!is.na(beers$score_style), ]
beers <- beers[!is.na(beers$abv), ]

# create scaled categorical variables from the numbers
labels = c("low", "med_low", "med_high", "high")

scaled_score <- scale(beers$score)
bins <- quantile(scaled_score)
score <- cut(scaled_score, breaks = bins, include.lowest = TRUE, label = labels)
beers <- dplyr::select(beers, -score)
beers <- data.frame(beers, score)

scaled_style <- scale(beers$score_style)
bins <- quantile(scaled_style)
score_style <- cut(scaled_style, breaks = bins, include.lowest = TRUE, label = labels)
beers <- dplyr::select(beers, -score_style)
beers <- data.frame(beers, score_style)

scaled_abv <- scale(beers$abv)
bins <- quantile(scaled_abv)
abv <- cut(scaled_abv, breaks = bins, include.lowest = TRUE, label = labels)
beers <- dplyr::select(beers, -abv)
beers <- data.frame(beers, abv)

scaled_calories <- scale(beers$calories)
bins <- quantile(scaled_calories)
calories <- cut(scaled_calories, breaks = bins, include.lowest = TRUE, label = labels)
beers <- dplyr::select(beers, -calories)
beers <- data.frame(beers, calories)

scaled_ratings <- scale(beers$ratings)
bins <- quantile(scaled_ratings)
ratings <- cut(scaled_ratings, breaks = bins, include.lowest = TRUE, label = labels)
beers <- dplyr::select(beers, -ratings)
beers <- data.frame(beers, ratings)

scaled_weighted <- scale(beers$weighted_avg)
bins <- quantile(scaled_weighted)
weighted_avg_score <- cut(scaled_weighted, breaks = bins, include.lowest = TRUE, label = labels)
beers <- dplyr::select(beers, -weighted_avg_score)
beers <- data.frame(beers, weighted_avg_score)

# change styles column name to style
colnames(beers)[5] <- "style"

# set row names to beer names
row.names(beers) <- beers$X
beers[1] = NULL

write.csv(beers, file="wrangled_beers.csv")
