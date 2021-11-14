info <- httr::GET("https://api.github.com/repos/mestevez1966/t/git/trees/main?recursive=1")

info_json <- httr::content(info, as = "parsed")
info_json <- jsonlite::fromJSON(jsonlite::toJSON(info_json))

files <- unlist(info_json$tree$path)

files <- files[grepl("salidas_api_twitter/polaridad/", x = files)]
files <- files[grepl(".csv", x = files)]
file <- vector("list", length = length(files))

for(i in 1:length(files)) {
  
  file[[i]] <- read.csv(paste0("https://github.com/mestevez1966/t/blob/main/", files[i], "?raw=true"))
  
}

output <- do.call(plyr::rbind.fill, lapply(file, as.data.frame))

output$Polaridad <- ifelse(grepl("'polarity': 'P'", output$code), 4, 
                     ifelse(grepl("'polarity': 'P+'", output$code), 5, 
                     ifelse(grepl("'polarity': 'NEU'", output$code), 2,
                     ifelse(grepl("'polarity': 'NONE'", output$code), 3, 
                     ifelse(grepl("'polarity': 'N'", output$code), 2,
                     ifelse(grepl("'polarity': 'N+'", output$code), 1, ""))))))

ruta <- "/salidas_api_twitter/polaridad/merged/merged.csv"

write.csv2(output, ruta)
