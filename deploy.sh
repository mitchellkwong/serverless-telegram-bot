# Features are deployed as seperate functions to track feature level analytics.
# A router redirect requests to the webhook endpoint to endpoints for each feature. 

# router redirects webhook requests to dedicated handlers
gcloud functions deploy router \
  --source cinnabot-test/github_mitchellkwong_serverless-telegram-bot/main// \
  --runtime python38 \
  # --env-vars-file env.yml \
  --trigger-http \
  --allow-unauthenticated

# echo repeats user messages
gcloud functions deploy echo \
  --source cinnabot-test/github_mitchellkwong_serverless-telegram-bot/main// \
  --runtime python38 \
  --env-vars-file env.yml \
  --trigger-http \
  --allow-unauthenticated
