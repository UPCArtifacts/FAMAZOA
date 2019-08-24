
---

<ul class="collapsible">
    <li>
      <div class="collapsible-header"><i class="material-icons">apps</i>Applications<span class="new badge" data-badge-caption="{{ page.number_of_apps }}"></span></div>
      <div class="collapsible-body">
        <div class="collection">
        {% for app in page.apps %}
        <a class="collection-item" target="_blank" href="{{ app.repo }}">{{ app.repo }}</a>
        {% endfor %}
        </div>
      </div>
    </li>
</ul>
