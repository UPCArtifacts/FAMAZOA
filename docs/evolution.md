---
layout: page
title: Evolution
permalink: /Evolution/
---

<h1 class="page-title">{{ page.title | escape }}</h1>

<div class="section">
</div>
<div class="divider"></div>

{% assign current =  site.versions | last %}
{% for version in site.versions reversed%}
    {% if current.label == version.label %}
<h5>{{ version.label }}<span class="new badge" data-badge-caption="Current Version"></span></h5>
<div class="row">
    {% endif %}

    {% if current.label != version.label %}
<h5>{{ version.label }}</h5>
<div class="row">   
        {% endif %}
    <div class="col12">

           <ul>
            <li>Number of applications: <em>{{ version.number_of_apps }}</em></li>
            {% if version.loc %}
                <li>Number of Lines of Code: <em>{{ version.loc }}</em></li>
            {% endif %}
            {% if version.total_pure_kotlin %}
                <li>Number of pure Kotlin apps:<em>{{ version.total_pure_kotlin }}</em></li>
            {% endif %}
            <li>Release data: <em>{{ version.date | date: "%b %d,  %Y"}}</em></li>
            <li><a class="right" href="{{ version.url }}"> More details</a></li>
           </ul>
         </div>

    {% if current.label == version.label %}
        <div class="col6">
        </div>
    {% endif %}

</div>

<div class="divider"></div>
{% endfor %}

