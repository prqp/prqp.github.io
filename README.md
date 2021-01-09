# prqp



### .prqp md engine

| element | md                  | example                                  |
| ------- | ------------------- | ---------------------------------------- |
| comment | `# [text]`          | `# hey hey hey`                          |
| heading | `=[level=1] [text]` | `= this is a h1`<br />`=2 this is an h2` |
| text    | `[text]`            | `yeah pretty boring`                     |
| image   | `{path}`            | `{cat.jpg}`<br />`{animals/deer.webp}`   |



#### paragraphs

void lines (`\n`) split paragraphs:

```
this
is
the
same
par, and will be displayed inline

this
is another par
```

