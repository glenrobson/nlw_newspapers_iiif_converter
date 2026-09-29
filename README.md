# NLW Newspaper IIIF Converter

The NLW Newspapers used to be available at:

https://damsssl.llgc.org.uk/iiif/newspapers/3100020.json

but it looks like this has disappeared so this creates IIIF manifests and collections for a NLW Newspaper. 

To run:

```
uv run nlw-iiif 3036868 
```

Generates newspaper in the Newspapers directory.

To test:

```
uv run pytest
```

Specific test:

```
 uv run pytest tests/test_issue.py::test_parse_title
```