Brave Web Search API
Introduction
Brave Web Search API is a REST API to query Brave Search and get back search results from the web. The following sections describe how to curate requests, including parameters and headers, to Brave Web Search API and get a JSON response back.

To try the API on a Free plan, you’ll still need to subscribe — you simply won’t be charged. Once subscribed, you can get an API key in the API Keys section.

Endpoints
Brave Search API exposes multiple endpoints for specific types of data, based on the level of your subscription. If you don’t see the endpoint you’re interested in, you may need to change your subscription.

https://api.search.brave.com/res/v1/web/search

Example
A request has to be made to the web search endpoint. An example CURL request is given below.



curl -s --compressed "https://api.search.brave.com/res/v1/web/search?q=brave+search" \
  -H "Accept: application/json" \
  -H "Accept-Encoding: gzip" \
  -H "X-Subscription-Token: <YOUR_API_KEY>"

The response specification for Web Search API can be seen in the WebSearchApiResponse model.

Next Steps
To learn what parameters are available and what responses can be expected while querying Brave Web Search API, please review the following pages:

Query Parameters
Request Headers
Response Headers
Response Objects
Brave Local Search API
Introduction
Brave Local Search API provides enrichments for location search results.

Access to Local API is available through the Pro plans.

Endpoints
Brave Local Search API is currently available at the following endpoints and exposes an API to get extra information about a location, including pictures and related web results.

https://api.search.brave.com/res/v1/local/pois

The endpoint supports batching and retrieval of extra information of up to 20 locations with a single request.

The local API also includes an endpoint to get an AI generated description for a location.

https://api.search.brave.com/res/v1/local/descriptions

Example
An initial request has to be made to web search endpoint with a given query. An example CURL request is given below.



curl -s --compressed "https://api.search.brave.com/res/v1/web/search?q=greek+restaurants+in+san+francisco" \
  -H "Accept: application/json" \
  -H "Accept-Encoding: gzip" \
  -H "X-Subscription-Token: <YOUR_API_KEY>"

If the query returns a list of locations, as in this case, each location result has an id field, which is a temporary ID that can be used to retrieve extra information about the location. An example from the locations result is given below.

{
  "locations": {
    "results": [
      {
        "id": "1520066f3f39496780c5931d9f7b26a6",
        "title": "Pangea Banquet Mediterranean Food"
      },
      {
        "id": "d00b153c719a427ea515f9eacf4853a2",
        "title": "Park Mediterranean Grill"
      },
      {
        "id": "4b943b378725432aa29f019def0f0154",
        "title": "The Halal Mediterranean Co."
      }
    ]
  }
}

The id value can be used to further fetch extra information about the location. An example request is given below.



curl -s --compressed "https://api.search.brave.com/res/v1/local/pois?ids=1520066f3f39496780c5931d9f7b26a6&ids=d00b153c719a427ea515f9eacf4853a2" \
  -H "accept: application/json" \
  -H "Accept-Encoding: gzip" \
  -H "x-subscription-token: <YOUR_API_KEY>"

An AI generated description associated with a location can be further fetched using the example below.



curl -s --compressed "https://api.search.brave.com/res/v1/local/descriptions?ids=1520066f3f39496780c5931d9f7b26a6&ids=d00b153c719a427ea515f9eacf4853a2" \
  -H "accept: application/json" \
  -H "Accept-Encoding: gzip" \
  -H "x-subscription-token: <YOUR_API_KEY>"

The response specification for Local Search API can be seen in the LocalPoiSearchApiResponse and LocalDescriptionsSearchApiResponse models.

Query Parameters
# Web Search API
This table lists the query parameters supported by the Web Search API. Some are required, but most are optional.

Parameter	Required	Type	Default	Description
q	true	string		
The user’s search query term. Query can not be empty. Maximum of 400 characters and 50 words in the query.

country	false	string	US	
The search query country, where the results come from.

The country string is limited to 2 character country codes of supported countries. For a list of supported values, see Country Codes.

search_lang	false	string	en	
The search language preference.

The 2 or more character language code for which the search results are provided. For a list of possible values, see Language Codes.

ui_lang	false	string	en-US	
User interface language preferred in response.

Usually of the format ‘<language_code>-<country_code>’. For more, see RFC 9110. For a list of supported values, see UI Language Codes.

count	false	number	20	
The number of search results returned in response.

The maximum is 20. The actual number delivered may be less than requested. Combine this parameter with offset to paginate search results.

offset	false	number	0	
The zero based offset that indicates number of search results per page (count) to skip before returning the result. The maximum is 9. The actual number delivered may be less than requested based on the query.

In order to paginate results use this parameter together with count. For example, if your user interface displays 20 search results per page, set count to 20 and offset to 0 to show the first page of results. To get subsequent pages, increment offset by 1 (e.g. 0, 1, 2). The results may overlap across multiple pages.

safesearch	false	string	moderate	
Filters search results for adult content.

The following values are supported:

off: No filtering is done.
moderate: Filters explicit content, like images and videos, but allows adult domains in the search results.
strict: Drops all adult content from search results.
freshness	false	string		
Filters search results by when they were discovered.

The following values are supported: - pd: Discovered within the last 24 hours. - pw: Discovered within the last 7 Days. - pm: Discovered within the last 31 Days. - py: Discovered within the last 365 Days… - YYYY-MM-DDtoYYYY-MM-DD: timeframe is also supported by specifying the date range e.g. 2022-04-01to2022-07-30.

text_decorations	false	bool	1	
Whether display strings (e.g. result snippets) should include decoration markers (e.g. highlighting characters).

spellcheck	false	bool	1	
Whether to spellcheck provided query. If the spellchecker is enabled, the modified query is always used for search. The modified query can be found in altered key from the query response model.

result_filter	false	string		
A comma delimited string of result types to include in the search response.

Not specifying this parameter will return back all result types in search response where data is available and a plan with the corresponding option is subscribed. The response always includes query and type to identify any query modifications and response type respectively.

Available result filter values are: - discussions - faq - infobox - news - query - summarizer - videos - web - locations

Example result filter param result_filter=discussions, videos returns only discussions, and videos responses. Another example where only location results are required, set the result_filter param to result_filter=locations.

goggles_id	false	string		
Goggles act as a custom re-ranking on top of Brave’s search index. For more details, refer to the Goggles repository. This parameter is deprecated. Please use the goggles parameter.

goggles	false	string		
Goggles act as a custom re-ranking on top of Brave’s search index. The parameter supports both a url where the Goggle is hosted or the definition of the goggle. For more details, refer to the Goggles repository.

units	false	string		
The measurement units. If not provided, units are derived from search country.

Possible values are: - metric: The standardized measurement system - imperial: The British Imperial system of units.

extra_snippets	false	bool		
A snippet is an excerpt from a page you get as a result of the query, and extra_snippets allow you to get up to 5 additional, alternative excerpts.

Only available under Free AI, Base AI, Pro AI, Base Data, Pro Data and Custom plans.

summary	false	bool		
This parameter enables summary key generation in web search results. This is required for summarizer to be enabled.


You can also optimise your search query by using search operators.

# Local Search API
This table lists the query parameters supported by the Local Search API. Some are required, but most are optional.

Parameter	Required	Type	Default	Description
ids	true	list[string]		
Unique identifier for the location. Ids can not be empty. Maximum of 20 ids per request. The parameter can be repeated to query for multiple ids.

search_lang	false	string	en	
The search language preference.

The 2 or more character language code for which the search results are provided. For a list of possible values, see Language Codes.

ui_lang	false	string	en-US	
User interface language preferred in response.

Usually of the format ‘<language_code>-<country_code>’. For more, see RFC 9110. For a list of supported values, see UI Language Codes.

units	false	string		
The measurement units. If not provided, units are derived from search country.

Possible values are: - metric: The standardized measurement system - imperial: The British Imperial system of units.

