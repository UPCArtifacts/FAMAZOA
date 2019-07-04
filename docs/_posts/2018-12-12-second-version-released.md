---
layout: post
categories: [new_version]
tag: [update]
---

{% assign version = site.versions | where: "v_id", "2" | first  %}

We are proud to announce **FAMAZOA {{ version.label }}** that has *{{ version.number_of_apps }}*. [Check it out!]({{ version.url }})
