library(httr)

info <- httr::GET("https://api.github.com/repos/mestevez1966/t/git/trees/main?recursive=1")

info_json <- content(info, as = "parsed")
info_json <- jsonlite::fromJSON(jsonlite::toJSON(info_json))

files <- unlist(info_json$tree$path)

files <- files[grepl("salidas_api_twitter/polaridad/", x = files)]
files <- files[grepl(".csv", x = files)]
file <- vector("list", length = length(files))

for(i in 1:length(files)) {
  
  file[[i]] <- read.csv(paste0("https://github.com/mestevez1966/t/blob/main/", files[i], "?raw=true"))
  
}

output <- do.call(plyr::rbind.fill, lapply(file, as.data.frame))

ruta <- "/salidas_api_twitter/polaridad/merged/merged.xlsx"

write.csv2(output, ruta)





