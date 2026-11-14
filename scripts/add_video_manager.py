#!/usr/bin/env python3
"""
Adiciona painel admin para gerenciar os videos dos cursos.
Permite:
- Trocar videos do YouTube pelos proprios (URL ou upload)
- Definir video por curso/modulo
- Suporta 3 formatos:
  1. YouTube URL (padrao)
  2. Vimeo URL
  3. Arquivo MP4 proprio (upload)
"""
import re
from pathlib import Path

VIDEO_MANAGER_HTML = '''
<!-- ========== VIDEO MANAGER (apenas admin) ========== -->
<div id="videoManagerModal" class="vm-modal" style="display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.85);z-index:10000;align-items:center;justify-content:center;padding:20px;overflow-y:auto;">
  <div style="background:white;max-width:1000px;width:100%;border-radius:20px;padding:32px;max-height:90vh;overflow-y:auto;">

    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:24px;">
      <div>
        <h2 style="margin:0;font-family:'Playfair Display',serif;color:#0f766e;font-size:28px;">🎬 Gerenciador de Vídeos</h2>
        <p style="margin:4px 0 0;color:#64748b;font-size:14px;">Substitua os vídeos do YouTube pelos seus próprios</p>
      </div>
      <button onclick="closeVideoManager()" style="background:#fee2e2;border:none;color:#dc2626;width:36px;height:36px;border-radius:50%;font-size:20px;cursor:pointer;font-weight:700;">×</button>
    </div>

    <!-- Fonte do video -->
    <div style="background:#f0fdfa;padding:20px;border-radius:12px;margin-bottom:24px;">
      <h3 style="margin-top:0;color:#0f766e;font-size:16px;">📹 Fonte do Vídeo</h3>
      <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:16px;">
        <label style="display:flex;align-items:center;gap:6px;cursor:pointer;padding:8px 14px;background:white;border-radius:8px;border:2px solid #14b8a6;">
          <input type="radio" name="videoSource" value="youtube" checked onchange="switchVideoSource('youtube')"> YouTube
        </label>
        <label style="display:flex;align-items:center;gap:6px;cursor:pointer;padding:8px 14px;background:white;border-radius:8px;border:2px solid #cbd5e1;">
          <input type="radio" name="videoSource" value="vimeo" onchange="switchVideoSource('vimeo')"> Vimeo
        </label>
        <label style="display:flex;align-items:center;gap:6px;cursor:pointer;padding:8px 14px;background:white;border-radius:8px;border:2px solid #cbd5e1;">
          <input type="radio" name="videoSource" value="custom" onchange="switchVideoSource('custom')"> Meu Arquivo MP4
        </label>
      </div>

      <!-- Input YouTube -->
      <div id="youtubeInput">
        <label style="display:block;font-size:13px;font-weight:600;color:#475569;margin-bottom:6px;">Cole a URL ou ID do YouTube:</label>
        <div style="display:flex;gap:8px;">
          <input type="text" id="youtubeUrl" placeholder="https://www.youtube.com/watch?v=ABC123 ou ABC123" style="flex:1;padding:10px;border:1px solid #cbd5e1;border-radius:8px;font-size:13px;">
          <button onclick="previewVideo()" style="background:#dc2626;color:white;border:none;border-radius:8px;padding:10px 20px;font-weight:600;cursor:pointer;">▶ Preview</button>
        </div>
        <p style="margin:8px 0 0;font-size:11px;color:#94a3b8;">💡 Suporta URLs completas do YouTube, encurtadas (youtu.be), ou apenas o ID de 11 caracteres</p>
      </div>

      <!-- Input Vimeo -->
      <div id="vimeoInput" style="display:none;">
        <label style="display:block;font-size:13px;font-weight:600;color:#475569;margin-bottom:6px;">Cole a URL do Vimeo:</label>
        <input type="text" id="vimeoUrl" placeholder="https://vimeo.com/123456789" style="width:100%;padding:10px;border:1px solid #cbd5e1;border-radius:8px;font-size:13px;">
      </div>

      <!-- Input Custom Upload -->
      <div id="customInput" style="display:none;">
        <label style="display:block;font-size:13px;font-weight:600;color:#475569;margin-bottom:6px;">Faça upload do seu vídeo MP4:</label>
        <div style="border:2px dashed #14b8a6;background:white;padding:24px;border-radius:12px;text-align:center;cursor:pointer;" onclick="document.getElementById('videoFile').click()">
          <div style="font-size:32px;margin-bottom:8px;">📤</div>
          <div style="font-weight:600;color:#0f766e;margin-bottom:4px;">Clique para selecionar o vídeo</div>
          <div style="font-size:11px;color:#94a3b8;">MP4, WebM ou OGV (até 500MB)</div>
        </div>
        <input type="file" id="videoFile" accept="video/*" style="display:none;" onchange="handleVideoUpload(this)">
        <div id="uploadStatus" style="margin-top:12px;display:none;background:#d1fae5;padding:12px;border-radius:8px;font-size:13px;"></div>
        <p style="margin:8px 0 0;font-size:11px;color:#94a3b8;">💡 O vídeo é salvo como Base64 no navegador (localStorage). Suporta arquivos até ~50MB para melhor performance.</p>
      </div>

      <!-- Preview -->
      <div id="videoPreview" style="display:none;margin-top:16px;background:black;border-radius:12px;overflow:hidden;aspect-ratio:16/9;">
        <iframe id="previewFrame" width="100%" height="100%" frameborder="0" allowfullscreen></iframe>
      </div>
    </div>

    <!-- Lista de cursos/modulos -->
    <h3 style="color:#0f766e;font-size:16px;margin-bottom:12px;">📚 Atribuir Vídeo a Cada Módulo</h3>
    <div id="videoAssignmentList" style="display:grid;gap:10px;">
      <!-- Gerado dinamicamente -->
    </div>

    <!-- Botoes de acao -->
    <div style="display:flex;justify-content:space-between;gap:12px;margin-top:24px;padding-top:20px;border-top:1px solid #e2e8f0;">
      <button onclick="resetAllVideos()" style="background:#fee2e2;color:#dc2626;border:none;border-radius:8px;padding:12px 20px;font-weight:600;cursor:pointer;">🔄 Resetar Tudo para YouTube</button>
      <div style="display:flex;gap:12px;">
        <button onclick="closeVideoManager()" style="background:#cbd5e1;color:#1e293b;border:none;border-radius:8px;padding:12px 20px;font-weight:600;cursor:pointer;">Cancelar</button>
        <button onclick="saveVideoConfig()" style="background:linear-gradient(135deg,#14b8a6,#0d9488);color:white;border:none;border-radius:8px;padding:12px 24px;font-weight:700;cursor:pointer;">💾 Salvar Alterações</button>
      </div>
    </div>

  </div>
</div>

<!-- Botao para abrir o gerenciador (apenas admin) -->
<div id="videoManagerBtn" style="position:fixed;bottom:24px;right:24px;z-index:9999;display:none;">
  <button onclick="openVideoManager()" style="background:linear-gradient(135deg,#dc2626,#b91c1c);color:white;border:none;border-radius:50px;padding:14px 24px;font-weight:700;cursor:pointer;box-shadow:0 8px 24px rgba(220,38,38,0.4);font-size:14px;">
    🎬 Gerenciar Vídeos
  </button>
</div>

<script>
// ========== VIDEO MANAGER ==========
function openVideoManager() {
  document.getElementById('videoManagerModal').style.display = 'flex';
  loadVideoConfig();
  renderAssignmentList();
}

function closeVideoManager() {
  document.getElementById('videoManagerModal').style.display = 'none';
}

function switchVideoSource(source) {
  document.getElementById('youtubeInput').style.display = source === 'youtube' ? 'block' : 'none';
  document.getElementById('vimeoInput').style.display = source === 'vimeo' ? 'block' : 'none';
  document.getElementById('customInput').style.display = source === 'custom' ? 'block' : 'none';
  document.getElementById('videoPreview').style.display = 'none';
}

function extractYoutubeId(url) {
  if (!url) return null;
  url = url.trim();
  // ID puro (11 chars)
  if (/^[a-zA-Z0-9_-]{11}$/.test(url)) return url;
  // URL completa
  const match = url.match(/(?:youtube\\.com\\/(?:watch\\?v=|embed\\/)|youtu\\.be\\/)([a-zA-Z0-9_-]{11})/);
  return match ? match[1] : null;
}

function previewVideo() {
  const url = document.getElementById('youtubeUrl').value;
  const videoId = extractYoutubeId(url);
  if (!videoId) {
    alert('URL inválida! Cole uma URL completa do YouTube ou apenas o ID de 11 caracteres.');
    return;
  }
  const preview = document.getElementById('videoPreview');
  const frame = document.getElementById('previewFrame');
  frame.src = `https://www.youtube.com/embed/${videoId}`;
  preview.style.display = 'block';
}

function handleVideoUpload(input) {
  const file = input.files[0];
  if (!file) return;

  if (file.size > 50 * 1024 * 1024) {
    alert('Arquivo muito grande (>50MB). Recomendamos arquivos menores para melhor performance.');
    return;
  }

  const status = document.getElementById('uploadStatus');
  status.style.display = 'block';
  status.innerHTML = '⏳ Carregando arquivo...';

  const reader = new FileReader();
  reader.onload = (e) => {
    const dataUrl = e.target.result;
    // Preview
    const preview = document.getElementById('videoPreview');
    preview.innerHTML = `<video controls style="width:100%;height:100%;"><source src="${dataUrl}" type="${file.type}"></video>`;
    preview.style.display = 'block';
    status.innerHTML = `✅ Arquivo carregado: ${file.name} (${(file.size/1024/1024).toFixed(2)} MB)`;
    // Salva temporariamente
    window._pendingVideoData = { name: file.name, type: file.type, data: dataUrl };
  };
  reader.readAsDataURL(file);
}

function getVideoConfig() {
  const stored = localStorage.getItem('auxf_video_config');
  return stored ? JSON.parse(stored) : {};
}

function saveVideoConfigToStorage(config) {
  localStorage.setItem('auxf_video_config', JSON.stringify(config));
}

function loadVideoConfig() {
  return getVideoConfig();
}

function renderAssignmentList() {
  const config = getVideoConfig();
  const list = document.getElementById('videoAssignmentList');
  const cursos = [
    { id: 'antihipertensivos', title: 'Anti-hipertensivos', modulos: 7 },
    { id: 'antidiabeticos', title: 'Antidiabéticos', modulos: 7 },
  ];

  let html = '';
  cursos.forEach(curso => {
    html += `<div style="background:#f8fafc;padding:14px;border-radius:10px;border-left:4px solid #14b8a6;">
      <div style="font-weight:700;color:#0f766e;margin-bottom:10px;">📚 ${curso.title}</div>`;

    for (let i = 0; i < curso.modulos; i++) {
      const key = `${curso.id}_${i}`;
      const video = config[key] || { source: 'youtube', id: getDefaultVideoId(i) };

      html += `<div style="display:flex;gap:8px;align-items:center;margin-bottom:8px;background:white;padding:8px;border-radius:8px;">
        <span style="font-size:11px;color:#94a3b8;min-width:60px;">Módulo ${i+1}</span>
        <select onchange="changeVideoType('${key}', this.value)" style="padding:6px;border:1px solid #cbd5e1;border-radius:6px;font-size:11px;">
          <option value="youtube" ${video.source === 'youtube' ? 'selected' : ''}>YouTube</option>
          <option value="vimeo" ${video.source === 'vimeo' ? 'selected' : ''}>Vimeo</option>
          <option value="custom" ${video.source === 'custom' ? 'selected' : ''}>Meu MP4</option>
        </select>
        <input type="text" id="video_${key}" value="${video.source === 'custom' ? video.name : video.id}" placeholder="ID ou URL" style="flex:1;padding:6px 10px;border:1px solid #cbd5e1;border-radius:6px;font-size:11px;">
      </div>`;
    }
    html += '</div>';
  });

  list.innerHTML = html;
}

function getDefaultVideoId(idx) {
  const defaults = ['_Ps_bAvH5PU','eCS2tnZCbrs','6rywLQY5Klc','hCqUHvif2qI','2iH2hL07a7A','xtjCMasE6G4','TT9KfaOk-JU'];
  return defaults[idx % defaults.length];
}

function changeVideoType(key, source) {
  // Auto-foca o input
  const input = document.getElementById(`video_${key}`);
  input.placeholder = source === 'custom' ? 'Nome do arquivo' : 'ID ou URL';
}

function saveVideoConfig() {
  const config = {};
  const inputs = document.querySelectorAll('[id^="video_"]');
  inputs.forEach(input => {
    const key = input.id.replace('video_', '');
    const select = input.previousElementSibling;
    const source = select.value;
    config[key] = {
      source: source,
      id: input.value,
      data: source === 'custom' && window._pendingVideoData ? window._pendingVideoData.data : null,
      name: source === 'custom' ? input.value : null
    };
  });
  saveVideoConfigToStorage(config);
  alert('✅ Configuração salva! Recarregue a página para ver as mudanças.');
  closeVideoManager();
}

function resetAllVideos() {
  if (!confirm('Resetar todos os vídeos para os originais do YouTube?')) return;
  localStorage.removeItem('auxf_video_config');
  window._pendingVideoData = null;
  renderAssignmentList();
}

// Override do player para usar videos customizados
function getVideoForModule(cursoId, moduleIdx) {
  const config = getVideoConfig();
  const key = `${cursoId}_${moduleIdx}`;
  const video = config[key];

  if (!video) return null;

  if (video.source === 'youtube') {
    return `https://www.youtube.com/embed/${extractYoutubeId(video.id) || video.id}`;
  } else if (video.source === 'vimeo') {
    const id = video.id.match(/vimeo\\.com\\/(\\d+)/)?.[1] || video.id;
    return `https://player.vimeo.com/video/${id}`;
  } else if (video.source === 'custom' && video.data) {
    return video.data; // data URL
  }
  return null;
}

// Hook no openCourse para mostrar botao admin
const _origOpenCourseVM = window.openCourse;
if (typeof _origOpenCourseVM === 'function') {
  window.openCourse = function(cursoId) {
    _origOpenCourseVM.apply(this, arguments);
    // Mostra botao admin se for admin
    const user = JSON.parse(localStorage.getItem('auxf_session') || '{}');
    if (user.role === 'admin') {
      document.getElementById('videoManagerBtn').style.display = 'block';
    }
  };
}
</script>
'''


def main():
    output = Path("/workspace/output")

    arquivos = [
        "dashboard-auxfarmacia-FREE.html",
        "dashboard-auxfarmacia-PRO.html",
        "dashboard-auxfarmacia-PREMIUM.html",
        "dashboard-auxfarmacia-ENTERPRISE.html",
        "dashboard-auxfarmacia.html",
        "dashboard-auxfarmacia-educativo.html",
    ]

    print("=" * 60)
    print("🎬 Adicionando Gerenciador de Videos (apenas admin)")
    print("=" * 60)

    for fname in arquivos:
        path = output / fname
        if not path.exists():
            continue

        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()

        if 'videoManagerModal' not in html:
            html = html.replace('</body>', VIDEO_MANAGER_HTML + '\n</body>', 1)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ {fname}")

    print()
    print("=" * 60)
    print("✅ Video Manager adicionado!")
    print("=" * 60)


if __name__ == "__main__":
    main()