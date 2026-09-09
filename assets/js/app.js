/* ============ AI 情报站 — 渲染与筛选逻辑 ============ */
(function () {
  'use strict';

  var DATA = window.RADAR_DATA;
  if (!DATA) {
    document.getElementById('update-chip').textContent = '数据加载失败';
    return;
  }

  var state = {
    tab: 'models',
    ability: 'overall',
    access: 'all',
    scene: 'all',
    toolCat: 'all',
  };

  var ABILITY_META = {
    overall:  { label: '综合',     scale: 100, type: 'bench', cost: false },
    coding:   { label: '编程开发', scale: 100, type: 'bench', cost: false },
    logic:    { label: '逻辑推理', scale: 100, type: 'bench', cost: false },
    ppt_html: { label: 'PPT/HTML', scale: 10,  type: 'grade', cost: false },
    vision:   { label: '视觉',     scale: 10,  type: 'grade', cost: false },
    audio:    { label: '语音多模态', scale: 10, type: 'grade', cost: false },
    cost:     { label: '成本 ¥',   scale: 0,   type: 'cost', cost: true },
  };

  var AB_SHORT = {
    overall: '综合', coding: '编程', logic: '逻辑',
    ppt_html: 'PPT', vision: '视觉', audio: '语音',
  };

  function scoreText(model, key) {
    if (key === 'cost') {
      if (!model.price_cny) return '—';
      var avg = (model.price_cny.in + model.price_cny.out) / 2;
      return '¥' + avg.toFixed(1);
    }
    var a = model.abilities && model.abilities[key];
    if (!a || a.score == null) return '—';
    return String(a.score);
  }
  function scoreSortVal(model, key) {
    if (key === 'cost') {
      if (!model.price_cny) return null;
      return (model.price_cny.in + model.price_cny.out) / 2;
    }
    var a = model.abilities && model.abilities[key];
    return a ? a.score : null;
  }
  function abilitySrc(model, key) {
    if (key === 'cost') return '官方定价 × 汇率 ' + (DATA.meta.fx_usd_cny || '?');
    var a = model.abilities && model.abilities[key];
    return (a && a.src) || '';
  }

  function crownOf(rank) { return rank === 1 ? '👑' : rank === 2 ? '⚓' : rank === 3 ? '🏴‍☠️' : ''; }

  /* ---- 模型榜：纵列 + 排名放大 ---- */
  function renderModels() {
    var grid = document.getElementById('model-grid');
    var list = DATA.models.slice();

    if (state.access !== 'all') {
      list = list.filter(function (m) { return m.access === state.access; });
    }
    list.sort(function (a, b) {
      var va = scoreSortVal(a, state.ability);
      var vb = scoreSortVal(b, state.ability);
      if (va == null && vb == null) return 0;
      if (va == null) return 1;
      if (vb == null) return -1;
      return state.ability === 'cost' ? va - vb : vb - va;
    });

    if (list.length === 0) {
      grid.innerHTML = '<p style="color:var(--text-dim)">无匹配模型。</p>';
      return;
    }

    var meta = ABILITY_META[state.ability];
    var isGrade = meta.type === 'grade';
    var isCost = meta.type === 'cost';

    grid.innerHTML = list.map(function (m, i) {
      var rank = i + 1;
      var accessCls = m.access === 'direct' ? 'access-direct' : 'access-vpn';
      var accessTxt = m.access === 'direct' ? '🟢 国内直连' : '🔴 需翻墙';
      var topCls = rank === 1 ? 'top1' : (rank === 2 || rank === 3 ? 'top2' : '');
      var crown = crownOf(rank);

      var bountyVal = scoreText(m, state.ability);
      var bountySrc = abilitySrc(m, state.ability);

      // 能力小标签（一行）
      var abChips = ['overall', 'coding', 'logic', 'ppt_html', 'vision', 'audio'].map(function (k) {
        var v = scoreText(m, k);
        var na = v === '—';
        var hl = k === state.ability;
        return '<span class="ab-chip' + (hl ? ' hl' : '') + (na ? ' na' : '') + '">' + AB_SHORT[k] + ' ' + v + '</span>';
      }).join('');

      var priceLine = m.price_cny
        ? '¥' + m.price_cny.in + ' / ' + m.price_cny.out + ' 百万token'
        : '';

      var tags = [];
      if (m.open) tags.push('开源');
      tags.push(m.modality || '?');
      tags.push('上下文 ' + (m.ctx / 1000) + 'k');
      if (m.release) tags.push(m.release);

      return '' +
      '<div class="rank-row ' + topCls + '">' +
        '<div class="rank-num">' +
          (crown ? '<span class="crown">' + crown + '</span>' : '') +
          '<span class="no">NO.</span><span class="num">' + rank + '</span>' +
        '</div>' +
        '<div class="rank-main">' +
          '<div class="rank-name">' + m.name + '</div>' +
          '<div class="rank-vendor">' + m.vendor + ' · ' + m.country + '</div>' +
          '<div class="rank-abilities">' + abChips + '</div>' +
        '</div>' +
        '<div class="rank-bounty">' +
          '<div class="bounty-label">' + meta.label + (isGrade ? ' /10' : '') + '</div>' +
          '<div class="bounty-value">' + bountyVal + '</div>' +
          (bountySrc ? '<div class="bounty-src">' + bountySrc + '</div>' : '') +
        '</div>' +
        '<div class="rank-side">' +
          '<div class="rank-access ' + accessCls + '">' + accessTxt + '</div>' +
          (priceLine ? '<div class="rank-price">' + priceLine + '</div>' : '') +
          '<div class="rank-tags">' + tags.map(function (t) { return '<span class="tag">' + t + '</span>'; }).join('') + '</div>' +
          '<div class="rank-actions">' +
            '<a class="btn btn-primary" href="' + m.homepage + '" target="_blank" rel="noopener">官网 ↗</a>' +
            (m.docs ? '<a class="btn btn-ghost" href="' + m.docs + '" target="_blank" rel="noopener">文档</a>' : '') +
          '</div>' +
        '</div>' +
      '</div>';
    }).join('');
  }

  /* ---- Skill 列表（含场景筛选） ---- */
  var SCENE_LABEL = {
    agent: 'Agent 框架', coding: '编码开发', docs: '文档处理',
    tools: '工具集成', research: '内容采集', slides: '课件演示', design: '设计可视化',
    knowledge: '知识库',
  };

  function renderSkills() {
    var el = document.getElementById('skill-list');
    var list = DATA.skills.slice();
    if (state.scene !== 'all') {
      list = list.filter(function (s) { return s.scene === state.scene; });
    }
    list.sort(function (a, b) { return b.stars - a.stars; });

    if (list.length === 0) {
      el.innerHTML = '<p style="color:var(--text-dim)">该场景暂无收录的 skill。</p>';
      return;
    }

    el.innerHTML = list.map(function (s, i) {
      var sceneTxt = SCENE_LABEL[s.scene] || s.scene;
      return '' +
      '<div class="list-card">' +
        '<div class="stars-badge"><div class="num">' + formatStars(s.stars) + '</div><div class="lbl">⭐ STARS</div></div>' +
        '<div class="list-body">' +
          '<div class="list-title">' + s.name + ' <span class="repo">' + s.repo + '</span></div>' +
          '<div class="list-desc">' + s.desc + '</div>' +
          '<div class="list-meta"><span>#' + (i + 1) + '</span><span class="scene-tag">' + sceneTxt + '</span><span>语言：' + s.lang + '</span></div>' +
          '<div class="get-line">📥 获得方式：<b>' + s.get + '</b></div>' +
          '<div class="list-actions">' +
            '<a class="btn btn-primary" href="' + s.url + '" target="_blank" rel="noopener">GitHub ↗</a>' +
          '</div>' +
        '</div>' +
      '</div>';
    }).join('');
  }

  /* ---- Tool 列表（含分类筛选） ---- */
  var TOOL_CAT_LABEL = {
    local: '本地部署', platform: '应用平台', agent: 'Agent 平台', ui: '界面客户端', sdk: '框架 SDK',
  };

  function renderTools() {
    var el = document.getElementById('tool-list');
    var list = DATA.tools.slice();
    if (state.toolCat !== 'all') {
      list = list.filter(function (t) { return t.cat === state.toolCat; });
    }
    list.sort(function (a, b) { return b.stars - a.stars; });

    if (list.length === 0) {
      el.innerHTML = '<p style="color:var(--text-dim)">该分类暂无收录的工具。</p>';
      return;
    }

    el.innerHTML = list.map(function (t, i) {
      var catTxt = TOOL_CAT_LABEL[t.cat] || t.cat;
      return '' +
      '<div class="list-card">' +
        '<div class="stars-badge"><div class="num">' + formatStars(t.stars) + '</div><div class="lbl">⭐ STARS</div></div>' +
        '<div class="list-body">' +
          '<div class="list-title">' + t.name + ' <span class="repo">' + t.repo + '</span></div>' +
          '<div class="list-desc">' + t.desc + '</div>' +
          '<div class="list-meta"><span>#' + (i + 1) + '</span><span class="scene-tag">' + catTxt + '</span><span>语言：' + t.lang + '</span></div>' +
          '<div class="get-line">📥 获得方式：<b>' + t.get + '</b></div>' +
          '<div class="list-actions">' +
            '<a class="btn btn-primary" href="' + t.url + '" target="_blank" rel="noopener">官网 ↗</a>' +
            '<a class="btn btn-ghost" href="' + t.repo_url + '" target="_blank" rel="noopener">GitHub</a>' +
          '</div>' +
        '</div>' +
      '</div>';
    }).join('');
  }

  function formatStars(n) {
    if (n >= 1000) return (n / 1000).toFixed(0) + 'k';
    return String(n);
  }

  /* ---- 头部与 footer ---- */
  function renderHeader() {
    document.getElementById('update-chip').textContent = '数据更新于 ' + DATA.meta.generated;
    document.getElementById('fx-chip').textContent = '汇率 1 USD = ' + DATA.meta.fx_usd_cny + ' CNY (' + DATA.meta.fx_date + ')';
    var src = DATA.meta.sources;
    document.getElementById('footer-sources').innerHTML =
      '<b>数据来源</b>：' + src.source_bench_aa + ' ｜ ' + src.source_bench_swe + ' ｜ ' +
      src.source_bench_gpqa + ' ｜ 价格 ' + src.source_price + ' ｜ GitHub 星数 ' +
      (DATA.meta.github_updated ? '（查询于 ' + DATA.meta.github_updated + '，skills ' + DATA.meta.skill_count + ' / tools ' + DATA.meta.tool_count + ' 个）' : '') +
      ' ｜ 汇率 ' + src.fx_date;
  }

  /* ---- Tab 切换 ---- */
  function switchTab(tab) {
    state.tab = tab;
    document.querySelectorAll('.tab-btn').forEach(function (b) {
      b.classList.toggle('active', b.dataset.tab === tab);
    });
    document.querySelectorAll('.tab-panel').forEach(function (p) {
      p.classList.toggle('active', p.id === 'tab-' + tab);
    });
  }

  /* ---- 事件绑定 ---- */
  function bind() {
    document.getElementById('tabs').addEventListener('click', function (e) {
      var btn = e.target.closest('.tab-btn');
      if (btn) switchTab(btn.dataset.tab);
    });
    document.getElementById('ability-filters').addEventListener('click', function (e) {
      var chip = e.target.closest('.chip');
      if (!chip) return;
      state.ability = chip.dataset.ability;
      document.querySelectorAll('#ability-filters .chip').forEach(function (c) { c.classList.remove('active'); });
      chip.classList.add('active');
      renderModels();
    });
    document.getElementById('access-filters').addEventListener('click', function (e) {
      var chip = e.target.closest('.chip');
      if (!chip) return;
      state.access = chip.dataset.access;
      document.querySelectorAll('#access-filters .chip').forEach(function (c) { c.classList.remove('active'); });
      chip.classList.add('active');
      renderModels();
    });
    document.getElementById('scene-filters').addEventListener('click', function (e) {
      var chip = e.target.closest('.chip');
      if (!chip) return;
      state.scene = chip.dataset.scene;
      document.querySelectorAll('#scene-filters .chip').forEach(function (c) { c.classList.remove('active'); });
      chip.classList.add('active');
      renderSkills();
    });
    document.getElementById('tool-filters').addEventListener('click', function (e) {
      var chip = e.target.closest('.chip');
      if (!chip) return;
      state.toolCat = chip.dataset.toolcat;
      document.querySelectorAll('#tool-filters .chip').forEach(function (c) { c.classList.remove('active'); });
      chip.classList.add('active');
      renderTools();
    });
  }

  /* ---- 初始化 ---- */
  renderHeader();
  renderModels();
  renderSkills();
  renderTools();
  bind();
})();
