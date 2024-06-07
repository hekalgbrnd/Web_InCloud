# Web---Cloud
gcloud builds submit --tag gcr.io/streamlit-application-425010/streamlit-application  --project=streamlit-application-425010

gcloud run deploy --image gcr.io/streamlit-application-425010/2streamlit-application --platform managed  --project=streamlit-application-425010 --allow-unauthenticated