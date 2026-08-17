let currentData = {
  main_caption: '',
  filter_mode: 'all',
  items: []
};

document.addEventListener('DOMContentLoaded', () => {
  loadCategories();

  document.getElementById('main-caption-editor').addEventListener('input', (e) => {
    currentData.main_caption = e.target.value;
    renderFBPreview();
  });
});

async function loadCategories() {
  try {
    const res = await fetch('/api/categories');
    const categories = await res.json();
    
    const container = document.getElementById('category-buttons');
    container.innerHTML = '';
    
    categories.forEach((cat, index) => {
      const btn = document.createElement('button');
      btn.className = `cat-btn ${index === 0 ? 'active' : ''}`;
      btn.innerHTML = `<span>🏌️</span> ${cat.name}`;
      btn.onclick = () => {
        document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById('category-url').value = cat.url;
      };
      container.appendChild(btn);
    });
  } catch (err) {
    console.error('Failed to load categories:', err);
  }
}

function triggerScrape(mode) {
  const categoryUrl = document.getElementById('category-url').value;
  if (!categoryUrl) {
    alert('กรุณาระบุ URL หมวดหมู่สินค้า');
    return;
  }
  scrapeCategory(categoryUrl, mode);
}

async function scrapeCategory(url, filterMode = 'all') {
  const fetchAllBtn = document.getElementById('fetch-all-btn');
  const fetchNewBtn = document.getElementById('fetch-new-btn');
  const statusText = document.getElementById('status-text');
  
  fetchAllBtn.disabled = true;
  fetchNewBtn.disabled = true;
  
  // Clear previous state
  currentData.items = [];
  renderWorkspace();
  
  const modeText = filterMode === 'new_only' ? 'กำลังดึงเฉพาะสินค้ามาใหม่ล่าสุด (New Clubs)...' : 'กำลังดึงสินค้าพร้อมขายทั้งหมด...';
  statusText.textContent = modeText;
  
  try {
    const res = await fetch('/api/scrape', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ category_url: url, filter_mode: filterMode })
    });
    
    const data = await res.json();
    
    if (!data.success) {
      alert('เกิดข้อผิดพลาดในการดึงข้อมูล: ' + data.error);
      return;
    }
    
    currentData.main_caption = data.main_caption;
    currentData.filter_mode = filterMode;
    currentData.items = data.items.map(item => ({
      ...item,
      selected: true
    }));
    
    document.getElementById('workspace').style.display = 'block';
    
    const summaryTitle = filterMode === 'new_only' 
      ? `🔥 ดึงสินค้ามาใหม่ล่าสุด (NEW): ${currentData.items.length} รายการ`
      : `ดึงข้อมูลสินค้าทั้งหมด: ${currentData.items.length} รายการพร้อมขาย`;
      
    const summarySubtext = filterMode === 'new_only'
      ? `เฉพาะสินค้าที่ติดป้าย (New) และยังไม่ SOLD OUT พร้อมสำหรับโพสต์โปรโมทสินค้าใหม่!`
      : `รวมสินค้าทั้งหมดที่ยังไม่ SOLD OUT พร้อมรูปภาพแรกและลิงค์รายละเอียด`;
      
    document.getElementById('result-summary').textContent = summaryTitle;
    document.getElementById('result-subtext').textContent = summarySubtext;
    document.getElementById('item-count-badge').textContent = currentData.items.length;
    
    renderWorkspace();
    
    if (currentData.items.length === 0) {
      const emptyMsg = filterMode === 'new_only' 
        ? 'ไม่พบสินค้ามาใหม่ (New) ในหมวดหมู่นี้ในขณะนี้ (หรือขายหมดแล้ว)'
        : 'ไม่พบสินค้าพร้อมขายในหมวดหมู่นี้ในขณะนี้';
      showToast(emptyMsg);
    } else {
      const msg = filterMode === 'new_only'
        ? `ดึงสินค้ามาใหม่ (New Clubs) สำเร็จ ${currentData.items.length} รายการ!`
        : `ดึงสินค้าทั้งหมดสำเร็จ ${currentData.items.length} รายการ!`;
      showToast(msg);
    }
    
  } catch (err) {
    alert('เกิดข้อผิดพลาดในการเชื่อมต่อเซิร์ฟเวอร์: ' + err.message);
  } finally {
    fetchAllBtn.disabled = false;
    fetchNewBtn.disabled = false;
    statusText.textContent = 'พร้อมใช้งาน';
  }
}

function renderWorkspace() {
  renderFBPreview();
  renderItemGrid();
  document.getElementById('main-caption-editor').value = currentData.main_caption;
}

function renderFBPreview() {
  document.getElementById('fb-main-caption-preview').textContent = currentData.main_caption;
  
  const gridContainer = document.getElementById('fb-photo-grid-preview');
  gridContainer.innerHTML = '';
  
  const activeItems = currentData.items.filter(i => i.selected);
  
  if (activeItems.length === 0) {
    gridContainer.innerHTML = '<div style="padding: 40px; text-align: center; color: #b0b3b8; width: 100%;">⚠️ ไม่พบสินค้าแสดงผลในขณะนี้</div>';
    return;
  }
  
  activeItems.forEach((item, index) => {
    const card = document.createElement('div');
    card.className = 'fb-photo-card';
    card.onclick = () => copyItemCaption(currentData.items.indexOf(item));
    
    const newTag = item.is_new ? `<div class="fb-photo-new-tag">✨ NEW</div>` : '';
    
    card.innerHTML = `
      <img src="${item.image_url}" alt="Product Photo" onerror="this.src='https://via.placeholder.com/300?text=No+Image'" />
      ${newTag}
      <div class="fb-photo-badge">📷 รูปที่ ${index + 1}</div>
    `;
    gridContainer.appendChild(card);
  });
}

function renderItemGrid() {
  const container = document.getElementById('item-grid-container');
  container.innerHTML = '';
  
  if (currentData.items.length === 0) {
    container.innerHTML = '<div style="grid-column: 1/-1; padding: 40px; text-align: center; color: var(--text-muted); background: var(--bg-card); border-radius: var(--radius-lg);">⚠️ ไม่พบสินค้าในหมวดหมู่นี้ หรือสินค้าขายหมดแล้ว</div>';
    return;
  }
  
  currentData.items.forEach((item, index) => {
    const card = document.createElement('div');
    card.className = `item-card ${item.is_new ? 'is-new-card' : ''}`;
    
    const newOverlay = item.is_new ? `<div class="badge-new-overlay">✨ NEW</div>` : '';
    const newBadgeLabel = item.is_new ? `<span style="background: rgba(245, 158, 11, 0.2); color: #f59e0b; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem;">✨ สินค้ามาใหม่</span>` : '';

    card.innerHTML = `
      <div class="item-card-header">
        <div class="item-thumb-wrapper">
          <img src="${item.image_url}" class="item-thumb" onerror="this.src='https://via.placeholder.com/100?text=No+Image'" />
          ${newOverlay}
        </div>
        <div class="item-meta">
          <div class="item-number">
            รูปที่ ${index + 1} ${newBadgeLabel}
          </div>
          <a href="${item.url}" target="_blank" class="item-title-link">🔗 ${item.title || item.url.split('/product/')[1] || item.url}</a>
        </div>
      </div>
      
      <textarea class="item-desc-textarea" id="item-desc-${index}" onchange="updateItemDesc(${index}, this.value)">${item.description}</textarea>
      
      <div class="item-card-actions">
        <label style="display: flex; align-items: center; gap: 6px; font-size: 0.85rem; cursor: pointer; color: var(--text-muted);">
          <input type="checkbox" ${item.selected ? 'checked' : ''} onchange="toggleItemSelection(${index}, this.checked)" /> รวมในโพสต์นี้
        </label>
        
        <div style="display: flex; gap: 6px;">
          <a href="${item.image_url}" target="_blank" class="btn-secondary" style="font-size: 0.8rem; padding: 6px 12px; text-decoration: none;">🖼️ รูปเต็ม</a>
          <button class="btn-secondary" style="font-size: 0.8rem; padding: 6px 12px;" onclick="copyItemCaption(${index})">📋 คัดลอกข้อความรูปนี้</button>
        </div>
      </div>
    `;
    container.appendChild(card);
  });
}

function updateItemDesc(index, newDesc) {
  currentData.items[index].description = newDesc;
  renderFBPreview();
}

function toggleItemSelection(index, isChecked) {
  currentData.items[index].selected = isChecked;
  renderFBPreview();
}

function switchTab(tabId, evt) {
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
  
  if (evt && evt.currentTarget) {
    evt.currentTarget.classList.add('active');
  }
  document.getElementById(tabId).classList.add('active');
}

function updateMainCaptionFromEditor() {
  currentData.main_caption = document.getElementById('main-caption-editor').value;
  renderFBPreview();
  showToast('บันทึกแคปชั่นหลักเรียบร้อยแล้ว!');
}

function copyMainCaption() {
  navigator.clipboard.writeText(currentData.main_caption);
  showToast('คัดลอกแคปชั่นหลัก (Main Caption) แล้ว!');
}

function copyItemCaption(index) {
  const item = currentData.items[index];
  const textToCopy = `${item.description}\n${item.url}`;
  navigator.clipboard.writeText(textToCopy);
  showToast(`คัดลอกข้อความสำหรับรูปที่ ${index + 1} แล้ว!`);
}

function copyAllCombinedCaptions() {
  let combined = `=== MAIN POST CAPTION ===\n\n${currentData.main_caption}\n\n` + "=".repeat(50) + "\n\n";
  
  const activeItems = currentData.items.filter(i => i.selected);
  activeItems.forEach((item, idx) => {
    const badge = item.is_new ? " [✨ NEW]" : "";
    combined += `--- PHOTO #${idx + 1}${badge} ---\n${item.description}\n${item.url}\n\n`;
  });
  
  navigator.clipboard.writeText(combined);
  showToast('คัดลอกข้อความทั้งหมดเรียบร้อยแล้ว!');
}

async function downloadZipPackage() {
  const activeItems = currentData.items.filter(i => i.selected);
  if (activeItems.length === 0) {
    alert('กรุณาเลือกอย่างน้อย 1 รายการเพื่อดาวน์โหลด');
    return;
  }
  
  showToast('กำลังเตรียมไฟล์ดาวน์โหลด (.ZIP)...');
  
  try {
    const res = await fetch('/api/download-zip', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        main_caption: currentData.main_caption,
        filter_mode: currentData.filter_mode,
        items: activeItems
      })
    });
    
    if (!res.ok) throw new Error('Download failed');
    
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const filePrefix = currentData.filter_mode === 'new_only' ? 'dns_golf_new_clubs_' : 'dns_golf_all_clubs_';
    a.download = `${filePrefix}${new Date().toISOString().slice(0,10)}.zip`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    
    showToast('ดาวน์โหลดไฟล์ .ZIP สำเร็จแล้ว!');
  } catch (err) {
    alert('เกิดข้อผิดพลาดในการดาวน์โหลด: ' + err.message);
  }
}

function showToast(message) {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.classList.add('show');
  setTimeout(() => {
    toast.classList.remove('show');
  }, 2500);
}
