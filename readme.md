# Simple RAG

This repositorie contains the implementation of a simple RAG infrastructure to implement a POC in a client.
The main ideia here is to start the project with the starter set up and show value (simplification in acessing relevant and updated documentation without issues.)

To get started running the project just run 

```./init.sh```

And the database will run alongside with the API offering the endpoints for document insertion and information retrieval.
All the testing here was done using postman to create and validate the solution. Ideally it should have testing files but I was unable to do it do limited time.

For the insert_content route use:
```
{
    "name":"ruandocini/rag",
    "documentation_path":"documentation"
}
```
As the body for the request to populate the DB

For the search_content route utilize:
```
##1
{
    "query":"What is SageMaker?"
}
##2
{
    "query":"What are all AWS regions where SageMaker is available?"
}
##3
{
    "query":"How to check if an endpoint is KMS encrypted?"
}
##4
{
    "query":"What are SageMaker Geospatial capabilities?"
}
```
