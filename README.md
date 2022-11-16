# sumamizationcs
---
Description:
- Azure offers a set of pretrained and preoptimized Cognitive Services for usual cognitive tasks like reading a text in a form, generate a voice from a script or interact with a human in a conversation. When working with long documents or paragraphs it is extremely useful to get a concise abstract, we now offer two flavors with extractive or abstractive phrasing. 

- The example covered below does a summary for a given long text in a abstractive way, this means it mainly understand the concepts of the text and then rephrases to tailor the output to the desired length (i.e. 8 phrases long). As of Nov2022 this service is in gated public preview. More details [here](https://learn.microsoft.com/en-us/azure/cognitive-services/language-service/summarization/overview?tabs=document-summarization) 

Languages:
- ![python](https://img.shields.io/badge/language-python-orange)

Products:
- Azure Cognitive Search
- Azure Cognitive Services
- Azure Functions
---

# Steps    

1. Create or reuse a Azure Cognitive Service Language Service. Creation can be done from the Azure portal or in [Language Studio](https://language.cognitive.azure.com/). As of Nov2022 it is still in Gated Public Preview so you will have to request access to the service
2. Get familiar with the Language service and try different lengths for your specific use case
3. Create a Python Function in Azure, for example this is a good [starting point](https://docs.microsoft.com/azure/azure-functions/create-first-function-vs-code-python)
4. Clone this repository
5. Open the folder in VS Code and deploy the function, find here a [tutorial](https://docs.microsoft.com/azure/search/cognitive-search-custom-skill-python)
6. Fill your Functions appsettings with the custom details from your deployment ('TA_ENDPOINT', 'TA_KEY') with the info you got in the Azure portal
7. Add a field in your index where you will dump the enriched entities, more info [here](#sample-index-field-definition)
8. Add the skill to your skillset as [described below](#sample-skillset-integration)
9. Add the output field mapping in your indexer as [seen in the sample](#sample-indexer-output-field-mapping)
10. Run the indexer 

## Sample Input:

You can find a sample input for the skill [here](../main/custom_ner/sample.dat)

```json
{
    "values": [
      {
        "recordId": "0",
        "data":
           {
            "text": "At Microsoft, we have been on a quest to advance AI beyond existing techniques, by taking a more holistic,human-centric approach to learning and understanding. As Chief Technology Officer of Azure AI CognitiveServices, I have been working with a team of amazing scientists and engineers to turn this quest into areality. In my role, I enjoy a unique perspective in viewing the relationship among three attributes ofhuman cognition: monolingual text (X), audio or visual sensory signals, (Y) and multilingual (Z). At theintersection of all three, there's magic-what we call XYZ-code as illustrated in Figure 1-a jointrepresentation to create more powerful AI that can speak, hear, see, and understand humans better.We believe XYZ-code will enable us to fulfill our long-term vision: cross-domain transfer learning,spanning modalities and languages. The goal is to have pretrained models that can jointly learnrepresentations to support a broad range of downstream AI tasks, much in the way humans do today.Over the past five years, we have achieved human performance on benchmarks in conversational speechrecognition, machine translation, conversational question answering, machine reading comprehension,and image captioning. These five breakthroughs provided us with strong signals toward our more ambitiousaspiration to produce a leap in AI capabilities, achieving multisensory and multilingual learning thatis closer in line with how humans learn and understand. I believe the joint XYZ-code is a foundationalcomponent of this aspiration, if grounded with external knowledge sources in the downstream AI tasks."
           }
      }
     
    ]
}
```

## Sample Output:

```json
{
    "values": [
        {
            "recordId": "0",
            "data": {
                "text": "{'text': 'Microsoft is taking a holistic,human-centric approach to learning and understanding. We believe XYZ-code will enable us to fulfill our long-term vision: cross-domain transfer learning, spanning modalities and languages. Over the past five years, we have achieved human performance on benchmarks in. conversational speechrecognition, machine translation,. conversational question answering, machine reading comprehension, and image captions. This is a step toward our more ambitiousaspiration to produce a leap in AI capabilities, achieving multisensory and multilingual learning thatis closer to how humans learn and understand.', 'contexts': [{'offset': 0, 'length': 1612}]}"
            }
        }
    ]
}
```

## Sample Skillset Integration

In order to use this skill in a cognitive search pipeline, you'll need to add a skill definition to your skillset.
Here's a sample skill definition for this example (inputs and outputs should be updated to reflect your particular scenario and skillset environment):

```json
    {
      "@odata.type": "#Microsoft.Skills.Custom.WebApiSkill",
      "name": "Summarization skill",
      "description": "Create a summary",
      "context": "/document",
      "uri": "https://x.azurewebsites.net/api/y?code=z==",
      "httpMethod": "POST",
      "timeout": "PT30S",
      "batchSize": 1,
      "degreeOfParallelism": null,
      "inputs": [
        {
          "name": "text",
          "source": "/document/content"
        }
      ],
      "outputs": [
        {
          "name": "text",
          "targetName": "summary"
        }
      ],
      "httpHeaders": {}
    }
```

## Sample Index Field Definition

The skill will output the summary extracted for the corpus. 

```json
  "fields": [
    {
      "name": "summary",
      "type": "Edm.String",
      "searchable": true,
      "filterable": false,
      "retrievable": true,
      "sortable": false,
      "facetable": false,
      "key": false,
      "indexAnalyzer": null,
      "searchAnalyzer": null,
      "analyzer": null,
      "normalizer": null,
      "synonymMaps": []
    },
```

## Sample Indexer Output Field Mapping

The output enrichment of your skill can be directly mapped to one of your fields described above. This can be done with the indexer setting:
```
  "outputFieldMappings": [
    {
      "sourceFieldName": "/document/summary",
      "targetFieldName": "summary"
    }
```
