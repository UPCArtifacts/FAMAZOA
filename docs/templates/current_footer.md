---


<h1 class="page-title">{{ page.title | escape }}</h1>

  <div class="card">
    <div class="card-content post-header">
        <span class="card-title post-title">{{ page.label | escape }}</span>
      <p class="post-meta">
      <time datetime="{{ page.date | date_to_xmlschema }}" itemprop="datePublished">
        {% assign date_format = site.minima.date_format | default: "%b %-d, %Y" %}
        Released in: {{ page.date | date: date_format }}
      </time>
      </p>
        
        {% assign online = 0 %}
        {% for app in page.apps %}
            {% if app.status >= 200 and app.status < 300 %}
                {% assign online = online | plus: 1 %}
            {% endif %}
        {% endfor %}
      <ul>
        <li>Number of applications: <em>{{ page.number_of_apps }}</em></li>
        <li>Repositories online: <em class="green-text">{{ online }}</em></li>
        <li>Last verified: <em>{{ page.last_update | date: date_format }}</em></li>
      </ul>

    </div>

    <div class="card-action">
        {% assign version = site.versions | where: "v_id", page.v_id | first %}
        {% assign download_url = "/assets" | append: version.url | append: ".txt" %}
        <a href="{{ download_url }}" target="_blank"><i class="material-icons">get_app</i> Download</a>
    </div>
  </div>

<ul class="collapsible">
    <li>
      <div class="collapsible-header"><i class="material-icons">apps</i>Applications</div>
      <div class="collapsible-body">
        <ul class="collection">
        {% for app in page.apps %}
        {% if app.status >= 200 and app.status < 300 %}
            {% assign status_icon = "link" %}
            {% assign color_icon = "green-text" %}
        {% elsif app.status >= 300 and app.status < 400 %}
            {% assign status_icon = "link_on" %}
            {% assign color_icon = "yellow-text" %}
        {% else  %}
            {% assign status_icon = "link_off" %}
            {% assign color_icon = "red-text text-lighten-1" %}
        {% endif %}
        <li class="collection-item"><div>{{ app.repo }}<a href="{{ app.repo }}" class="secondary-content"><i class="material-icons {{ color_icon }}">{{ status_icon }}</i></a></div></li>
        {% endfor %}
        </ul>
      </div>
    </li>
</ul>
  <div class="card">
    <div class="card-content post-header">
        <span class="card-title post-title">LOC</span>
      <p class="post-meta">
      <time datetime="{{ page.date | date_to_xmlschema }}" itemprop="datePublished">
        {% assign date_format = site.minima.date_format | default: "%b %-d, %Y" %}
        Released in: {{ page.date | date: date_format }}
      </time>
      </p>
      <div class="row">
        <div class="col s12 l6">
            <table>
                <thead>
                    <tr>
                        <th>Language</th>
                        <th>Files</th>
                        <th>Blank</th>
                        <th>Comment</th>
                        <th>Code</th>
                    </tr>
                </thead>
                <tbody>
                    {% for lang in page.languages %}
                    <tr data-lang="{{ lang.name }}">
                        <td>{{ lang.name }}</td>
                        <td>{{ lang.files }}</td> 
                        <td>{{ lang.blank }}</td>
                        <td>{{ lang.comment }}</td> 
                        <td data-code="{{ lang.code }}">{{ lang.code }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
          </table>
          <p class="detail">Provided by <a href="https://github.com/AlDanial/cloc" target="_blank">CLOC</a></p>
        </div>
         <div class="col s12 l6" id="pie">
        </div>

      </div>
   </div>
</div>
<!--
  <div class="card">
    <div class="card-content post-header">
        <span class="card-title post-title">Commits</span>
      <p class="post-meta">
      <time datetime="{{ page.date | date_to_xmlschema }}" itemprop="datePublished">
        {% assign date_format = site.minima.date_format | default: "%b %-d, %Y" %}
        Released in: {{ page.date | date: date_format }}
      </time>
      </p>
    </div>
</div>
-->

