#!/usr/bin/env python3
"""
Adiciona secao 'Biblioteca de Videos' dentro de cada modulo do curso.
Lista todos os videos complementares do YouTube que o aluno pode assistir.
"""
from pathlib import Path

VIDEO_LIBRARY_HTML = '''
<!-- ========== BIBLIOTECA DE VIDEOS ========== -->
<div class="video-library" style="margin:24px 0;background:linear-gradient(135deg,#f0fdfa 0%,#ccfbf1 100%);border-radius:16px;padding:24px;border:2px solid #14b8a6;">
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
    <div style="width:48px;height:48px;background:linear-gradient(135deg,#dc2626,#b91c1c);border-radius:12px;display:flex;align-items:center;justify-content:center;color:white;font-size:24px;">▶</div>
    <div>
      <h3 style="margin:0;font-family:Playfair Display,serif;color:#0f766e;">📺 Biblioteca de Videos Complementares</h3>
      <p style="margin:4px 0 0 0;font-size:13px;color:#0d9488;">Aulas em portugues, selecionadas de canais medicos verificados</p>
    </div>
  </div>

  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px;">

    <a href="https://www.youtube.com/watch?v=_Ps_bAvH5PU" target="_blank" rel="noopener" style="text-decoration:none;">
      <div style="background:white;padding:14px;border-radius:10px;border-left:4px solid #dc2626;cursor:pointer;transition:all 0.2s;" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
        <div style="display:flex;gap:10px;align-items:start;">
          <div style="background:#fef2f2;width:40px;height:40px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">🎬</div>
          <div style="flex:1;min-width:0;">
            <div style="font-weight:600;color:#7f1d1d;font-size:13px;margin-bottom:4px;">Educacao Farmaceutica - HAS</div>
            <div style="font-size:11px;color:#64748b;line-height:1.4;">Medicao correta da pressao + classificacao</div>
            <div style="display:inline-block;background:#dc2626;color:white;padding:2px 8px;border-radius:4px;font-size:10px;margin-top:6px;">⏱ 10:24</div>
          </div>
        </div>
      </div>
    </a>

    <a href="https://www.youtube.com/watch?v=eCS2tnZCbrs" target="_blank" rel="noopener" style="text-decoration:none;">
      <div style="background:white;padding:14px;border-radius:10px;border-left:4px solid #f59e0b;cursor:pointer;transition:all 0.2s;" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
        <div style="display:flex;gap:10px;align-items:start;">
          <div style="background:#fff7ed;width:40px;height:40px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">💊</div>
          <div style="flex:1;min-width:0;">
            <div style="font-weight:600;color:#92400e;font-size:13px;margin-bottom:4px;">HAS - Tratamento Farmacologico</div>
            <div style="font-size:11px;color:#64748b;line-height:1.4;">Aula completa sobre IECA, BRA, BCC, diureticos</div>
            <div style="display:inline-block;background:#f59e0b;color:white;padding:2px 8px;border-radius:4px;font-size:10px;margin-top:6px;">⏱ 20:15</div>
          </div>
        </div>
      </div>
    </a>

    <a href="https://www.youtube.com/watch?v=6rywLQY5Klc" target="_blank" rel="noopener" style="text-decoration:none;">
      <div style="background:white;padding:14px;border-radius:10px;border-left:4px solid #7c3aed;cursor:pointer;transition:all 0.2s;" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
        <div style="display:flex;gap:10px;align-items:start;">
          <div style="background:#f3e8ff;width:40px;height:40px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">⚡</div>
          <div style="flex:1;min-width:0;">
            <div style="font-weight:600;color:#5b21b6;font-size:13px;margin-bottom:4px;">Antihipertensivos Resumo - Flavonoid</div>
            <div style="font-size:11px;color:#64748b;line-height:1.4;">Resumo rapido para revisao de prova</div>
            <div style="display:inline-block;background:#7c3aed;color:white;padding:2px 8px;border-radius:4px;font-size:10px;margin-top:6px;">⏱ 15:30</div>
          </div>
        </div>
      </div>
    </a>

    <a href="https://www.youtube.com/watch?v=hCqUHvif2qI" target="_blank" rel="noopener" style="text-decoration:none;">
      <div style="background:white;padding:14px;border-radius:10px;border-left:4px solid #10b981;cursor:pointer;transition:all 0.2s;" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
        <div style="display:flex;gap:10px;align-items:start;">
          <div style="background:#d1fae5;width:40px;height:40px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">📚</div>
          <div style="flex:1;min-width:0;">
            <div style="font-weight:600;color:#065f46;font-size:13px;margin-bottom:4px;">Resumao HAS - Farmacologia Facil</div>
            <div style="font-size:11px;color:#64748b;line-height:1.4;">Todas as classes em uma aula so</div>
            <div style="display:inline-block;background:#10b981;color:white;padding:2px 8px;border-radius:4px;font-size:10px;margin-top:6px;">⏱ 45:00</div>
          </div>
        </div>
      </div>
    </a>

    <a href="https://www.youtube.com/watch?v=2iH2hL07a7A" target="_blank" rel="noopener" style="text-decoration:none;">
      <div style="background:white;padding:14px;border-radius:10px;border-left:4px solid #0ea5e9;cursor:pointer;transition:all 0.2s;" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
        <div style="display:flex;gap:10px;align-items:start;">
          <div style="background:#dbeafe;width:40px;height:40px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">🎓</div>
          <div style="flex:1;min-width:0;">
            <div style="font-weight:600;color:#1e3a8a;font-size:13px;margin-bottom:4px;">Farmacologia Clinica - USP</div>
            <div style="font-size:11px;color:#64748b;line-height:1.4;">Aula USP completa - algoritmo terapeutico</div>
            <div style="display:inline-block;background:#0ea5e9;color:white;padding:2px 8px;border-radius:4px;font-size:10px;margin-top:6px;">⏱ 60:00</div>
          </div>
        </div>
      </div>
    </a>

    <a href="https://www.youtube.com/watch?v=xtjCMasE6G4" target="_blank" rel="noopener" style="text-decoration:none;">
      <div style="background:white;padding:14px;border-radius:10px;border-left:4px solid #ec4899;cursor:pointer;transition:all 0.2s;" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
        <div style="display:flex;gap:10px;align-items:start;">
          <div style="background:#fce7f3;width:40px;height:40px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">🏥</div>
          <div style="flex:1;min-width:0;">
            <div style="font-weight:600;color:#831843;font-size:13px;margin-bottom:4px;">HAS - Reta Final Revalida</div>
            <div style="font-size:11px;color:#64748b;line-height:1.4;">Diagnostico e tratamento para residencia</div>
            <div style="display:inline-block;background:#ec4899;color:white;padding:2px 8px;border-radius:4px;font-size:10px;margin-top:6px;">⏱ 60:00</div>
          </div>
        </div>
      </div>
    </a>

    <a href="https://www.youtube.com/watch?v=cFroEnBv6-U" target="_blank" rel="noopener" style="text-decoration:none;">
      <div style="background:white;padding:14px;border-radius:10px;border-left:4px solid #6366f1;cursor:pointer;transition:all 0.2s;" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
        <div style="display:flex;gap:10px;align-items:start;">
          <div style="background:#e0e7ff;width:40px;height:40px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">⭐</div>
          <div style="flex:1;min-width:0;">
            <div style="font-weight:600;color:#3730a3;font-size:13px;margin-bottom:4px;">HAS Sistematica - Super Revisao</div>
            <div style="font-size:11px;color:#64748b;line-height:1.4;">Revisao sistematica para prova</div>
            <div style="display:inline-block;background:#6366f1;color:white;padding:2px 8px;border-radius:4px;font-size:10px;margin-top:6px;">⏱ 45:00</div>
          </div>
        </div>
      </div>
    </a>

    <a href="https://www.youtube.com/watch?v=TT9KfaOk-JU" target="_blank" rel="noopener" style="text-decoration:none;">
      <div style="background:white;padding:14px;border-radius:10px;border-left:4px solid #f97316;cursor:pointer;transition:all 0.2s;" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
        <div style="display:flex;gap:10px;align-items:start;">
          <div style="background:#fed7aa;width:40px;height:40px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">👶</div>
          <div style="flex:1;min-width:0;">
            <div style="font-weight:600;color:#7c2d12;font-size:13px;margin-bottom:4px;">HAS Pediatrica - CardioPedBrasil</div>
            <div style="font-size:11px;color:#64748b;line-height:1.4;">Hipertensao em criancas (curva P95)</div>
            <div style="display:inline-block;background:#f97316;color:white;padding:2px 8px;border-radius:4px;font-size:10px;margin-top:6px;">⏱ 30:45</div>
          </div>
        </div>
      </div>
    </a>

    <a href="https://www.youtube.com/watch?v=lUfxLq9nSkM" target="_blank" rel="noopener" style="text-decoration:none;">
      <div style="background:white;padding:14px;border-radius:10px;border-left:4px solid #be185d;cursor:pointer;transition:all 0.2s;" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
        <div style="display:flex;gap:10px;align-items:start;">
          <div style="background:#fce7f3;width:40px;height:40px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">🔬</div>
          <div style="flex:1;min-width:0;">
            <div style="font-weight:600;color:#831843;font-size:13px;margin-bottom:4px;">HAS Secundaria - Episodio 77</div>
            <div style="font-size:11px;color:#64748b;line-height:1.4;">Causas secundarias de hipertensao</div>
            <div style="display:inline-block;background:#be185d;color:white;padding:2px 8px;border-radius:4px;font-size:10px;margin-top:6px;">⏱ 30:00</div>
          </div>
        </div>
      </div>
    </a>

  </div>

  <div style="margin-top:16px;padding:12px;background:white;border-radius:8px;font-size:12px;color:#475569;text-align:center;">
    💡 <strong>Dica:</strong> Assista esses videos para aprofundar o conteudo. Clique em cada card para abrir no YouTube.
    <br><strong>+20 XP</strong> por video assistido (use o botao "✓ Marcar como assistida" no player principal).
  </div>
</div>
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
    print("📺 Adicionando Biblioteca de Videos complementares")
    print("=" * 60)

    for fname in arquivos:
        path = output / fname
        if not path.exists():
            continue

        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()

        # Adiciona antes do </body>, apenas uma vez
        if 'video-library' not in html:
            html = html.replace('</body>', VIDEO_LIBRARY_HTML + '\n</body>', 1)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ {fname}")

    print()
    print("=" * 60)
    print("✅ Biblioteca de videos adicionada!")
    print("=" * 60)


if __name__ == "__main__":
    main()