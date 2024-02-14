# Multiprocessing Example

Simple example and comparison of multiprocessing approach in Python.

## Why?
I found that using mp.Pool is very slow if processed data inside target is significantly different.

#### Example: Processing EDF files that varies from 5 minutes to 4 hours.

I read that Queue might solve this problem, so here is quick test.

## Output from script run on AMD Ryzen 7 5800H
```text
---Initialisation---
No data             RAM usage: 2.61658 GB
Data created        RAM usage: 14.74402 GB
---Start of Analysis---
No multiprocessing  RAM start: 14.74402 GB  RAM end: 14.82121 GB    Runtime: 3842.73287 sec
Trial: 0
Manager chunked     RAM start: 14.61993 GB  RAM end: 14.82646 GB    Runtime: 399.81491 sec
Pool map            RAM start: 14.77025 GB  RAM end: 15.06943 GB    Runtime: 296.58798 sec
Queue               RAM start: 14.86828 GB  RAM end: 15.33127 GB    Runtime: 73.48324 sec,  RAM processes created: 21.81398 GB
Manager             RAM start: 15.32964 GB  RAM end: 14.98455 GB    Runtime: 73.54095 sec,  RAM processes created: 21.67802 GB
Trial: 1
Manager chunked     RAM start: 14.98415 GB  RAM end: 14.94984 GB    Runtime: 399.81197 sec
Pool map            RAM start: 14.91455 GB  RAM end: 15.08916 GB    Runtime: 296.62397 sec
Queue               RAM start: 15.05076 GB  RAM end: 15.61736 GB    Runtime: 74.34908 sec,  RAM processes created: 22.01756 GB
Manager             RAM start: 15.62485 GB  RAM end: 15.10766 GB    Runtime: 74.00150 sec,  RAM processes created: 21.89351 GB
Trial: 2
Manager chunked     RAM start: 15.10724 GB  RAM end: 15.12354 GB    Runtime: 400.15202 sec
Pool map            RAM start: 15.08973 GB  RAM end: 15.28970 GB    Runtime: 296.88716 sec
Queue               RAM start: 15.11891 GB  RAM end: 15.59557 GB    Runtime: 73.90325 sec,  RAM processes created: 22.06683 GB
Manager             RAM start: 15.60073 GB  RAM end: 15.21938 GB    Runtime: 74.28938 sec,  RAM processes created: 21.89179 GB

```
