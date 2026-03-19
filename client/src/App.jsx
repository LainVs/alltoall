import React, { useState, useEffect, useMemo } from 'react';
import {
  Upload, FileText, CheckCircle, XCircle,
  Loader2, ArrowRight, X, Search, Settings2,
  ChevronRight, Download, RefreshCw, Settings,
  AlertTriangle, Loader, FolderOpen, Languages
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';

const TRANSLATIONS = {
  zh: {
    title: 'All to All',
    subtitle: '欢迎回来',
    dropFiles: '点击或拖拽文件到这里',
    browseFiles: '支持选择多个文件',
    addMore: '添加更多文件',
    searchPlaceholder: '搜索目标格式 (例如 docx, md, pdf...)',
    noCommonFormats: '选中的文件没有共同的支持格式',
    noMatches: '未找到匹配的格式',
    keepOriginalName: '保留原始文件名',
    advanced: '高级设置',
    convertTo: '转换为',
    converting: '正在转换...',
    success: '全部转换完成！文件已开始下载。',
    error: '转换失败，请检查文件后重试。',
    processing: '正在处理 {count} 个文件...',
    defaultTarget: '...',
    fetching: '正在由于后端启动较慢而同步支持格式...',
    noFormats: '未能从服务器获取到任何转换格式,请检查后端',
    catAll: '✨ 全部',
    catVideo: '🎬 视频',
    catAudio: '🎵 音频',
    catDoc: '📄 文档',
    catImage: '🖼️ 图片',
    catData: '📊 数据',
    setupTitle: '环境配置自检',
    setupSubtitle: '正在为您准备最轻盈、流畅的转换环境...',
    setupChecking: '正在检查系统依赖...',
    setupReady: '环境配置就绪！',
    setupMissing: '检测到缺失组件：',
    setupFix: '请安装上述组件后重新启动工具。',
    installing: '正在初始化转换引擎...',
    refresh: '重新检查环境',
  },
  en: {
    title: 'All to All',
    subtitle: 'Professional-grade file conversion suite.',
    dropFiles: 'Drop files here',
    browseFiles: 'or click to browse multiple files',
    addMore: 'Add more files',
    searchPlaceholder: 'Search target format (e.g. docx, md, pdf...)',
    noCommonFormats: 'No common formats found for selected files',
    noMatches: 'No matches found',
    keepOriginalName: 'Keep original filenames',
    advanced: 'Advanced',
    convertTo: 'Convert to',
    converting: 'Converting...',
    success: 'All conversions complete! Your files have been downloaded.',
    error: 'Conversion failed. Please check your files and try again.',
    processing: 'Converting {count} file(s)...',
    defaultTarget: '...',
    fetching: 'Fetching supported formats...',
    noFormats: 'No supported formats found from server.',
    catAll: '✨ All',
    catVideo: '🎬 Video',
    catAudio: '🎵 Audio',
    catDoc: '📄 Document',
    catImage: '🖼️ Image',
    catData: 'Data',
    setupTitle: 'Environment Check',
    setupSubtitle: 'Preparing a seamless conversion environment for you...',
    setupChecking: 'Checking system dependencies...',
    setupReady: 'Environment ready!',
    setupMissing: 'Missing components detected:',
    setupFix: 'Please install the above components and restart.',
    installing: 'Initializing engine...',
    refresh: 'Retry Check',
  }
};

const CATEGORIES = {
  catVideo: ['gif', 'mp4', 'mkv', 'mov', 'avi', 'flv', 'wmv', 'webm'],
  catAudio: ['mp3', 'wav', 'aac'],
  catDoc: ['docx', 'pdf', 'md', 'html', 'txt'],
  catImage: ['png', 'jpg'],
  catData: ['xlsx', 'csv', 'json'],
};

function App() {
  const [language, setLanguage] = useState('zh');
  const [files, setFiles] = useState([]);
  const [supportedFormats, setSupportedFormats] = useState({});
  const [selectedFile, setSelectedFile] = useState(null);
  const [targetFormat, setTargetFormat] = useState('');
  const [converting, setConverting] = useState(false);
  const [convertStatus, setConvertStatus] = useState({ type: '', message: '' });
  const [isLargeFile, setIsLargeFile] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('catAll');
  const [keepName, setKeepName] = useState(true);
  const [status, setStatus] = useState('idle'); // idle, uploading, success, error
  const [message, setMessage] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [isFetching, setIsFetching] = useState(true);
  const [systemStatus, setSystemStatus] = useState({ ready: true, missing_deps: [] });
  const [devicePref, setDevicePref] = useState('auto');

  const t = (key, params = {}) => {
    let text = TRANSLATIONS[language][key] || key;
    Object.keys(params).forEach(p => {
      text = text.replace(`{${p}}`, params[p]);
    });
    return text;
  };

  // 获取支持的格式
  const getFormats = async (retries = 3) => {
    setIsFetching(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/formats`);
      if (response.data.supported_formats) {
        setSupportedFormats(response.data.supported_formats);
        if (response.data.system_status) {
          setSystemStatus(response.data.system_status);
        }
      } else {
        // Fallback for old API if any
        setSupportedFormats(response.data);
      }
      setIsFetching(false);
      return true;
    } catch (error) {
      console.error('Failed to fetch formats:', error);
      if (retries > 0) {
        setTimeout(() => getFormats(retries - 1), 2000);
      } else {
        setIsFetching(false);
      }
      return false;
    }
  };

  useEffect(() => {
    getFormats();
  }, []);

  const onFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    addFiles(selectedFiles);
  };

  const addFiles = (newFiles) => {
    // 如果当前支持格式为空，尝试再次获取
    if (Object.keys(supportedFormats).length === 0) {
      getFormats(1);
    }

    setFiles(prev => {
      const combined = [...prev, ...newFiles];
      // 去重基于文件名
      return combined.filter((file, index, self) =>
        index === self.findIndex((f) => f.name === file.name)
      );
    });
  };

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const scanEntries = async (entries) => {
    const fileList = [];
    const readEntry = async (entry) => {
      if (entry.isFile) {
        const file = await new Promise((resolve) => entry.file(resolve));
        fileList.push(file);
      } else if (entry.isDirectory) {
        const reader = entry.createReader();
        const subEntries = await new Promise((resolve) => reader.readEntries(resolve));
        for (const subEntry of subEntries) {
          await readEntry(subEntry);
        }
      }
    };
    for (const entry of entries) {
      await readEntry(entry);
    }
    return fileList;
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    let droppedFiles = [];
    const items = e.dataTransfer.items;
    
    if (items && items[0].webkitGetAsEntry) {
      // Handle folders recursively
      const entries = Array.from(items)
        .map(item => item.webkitGetAsEntry())
        .filter(entry => entry !== null);
      droppedFiles = await scanEntries(entries);
    } else {
      droppedFiles = Array.from(e.dataTransfer.files);
    }

    if (droppedFiles.length > 0) {
      addFiles(droppedFiles);
      if (!selectedFile) setSelectedFile(droppedFiles[0]);
    }
  };

  // 根据当前文件列表计算可用的目标格式
  const availableTargetFormats = useMemo(() => {
    if (files.length === 0 || Object.keys(supportedFormats).length === 0) return [];

    // 获取所有文件的后缀
    const getExt = (filename) => {
      const parts = filename.split('.');
      if (parts.length > 1) return `.${parts.pop().toLowerCase()}`;
      return '';
    };

    const exts = files.map(f => getExt(f.name));

    // 找出所有文件共同支持的目标格式（交集）
    const getTargets = (ext) => {
      // 兼容性搜索：尝试匹配加点或不加点的格式
      if (supportedFormats[ext]) return supportedFormats[ext];
      // 尝试大小写不敏感匹配
      const key = Object.keys(supportedFormats).find(k => k.toLowerCase() === ext.toLowerCase());
      if (key) return supportedFormats[key];
      return [];
    };

    let intersection = getTargets(exts[0]);
    for (let i = 1; i < exts.length; i++) {
      const targets = getTargets(exts[i]);
      intersection = intersection.filter(fmt => targets.includes(fmt));
    }

    return [...new Set(intersection)].sort();
  }, [files, supportedFormats]);

  // 搜索和分类过滤后的格式
  const filteredFormats = useMemo(() => {
    let result = availableTargetFormats;
    
    // 1. 分类过滤
    if (selectedCategory !== 'catAll') {
      const allowedExts = CATEGORIES[selectedCategory];
      result = result.filter(fmt => {
        const cleanFmt = fmt.replace('.', '').toLowerCase();
        return allowedExts.includes(cleanFmt);
      });
    }

    // 2. 搜索词查询
    return result.filter(fmt => 
      fmt.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [availableTargetFormats, searchTerm, selectedCategory]);

  const handleConvert = async () => {
    if (files.length === 0 || !targetFormat) return;

    setIsUploading(true);
    setProgress(0);
    setStatus('uploading');
    setMessage(t('processing', { count: files.length }));

    const totalFiles = files.length;
    let successCount = 0;
    let simulatedInterval;

    try {
      // 对每个文件进行转换以展示真实进度
      for (let i = 0; i < files.length; i++) {
        const file = files[i];

        // 每个文件的进度区间
        const startProgress = (i / totalFiles) * 100;
        const endProgress = ((i + 1) / totalFiles) * 100;

        // 清除上一个文件的模拟计时器
        if (simulatedInterval) clearInterval(simulatedInterval);

        // 开启模拟增长：在该文件的 0% 到 90% 区间内缓慢增长
        let currentSimulated = 0;
        simulatedInterval = setInterval(() => {
          currentSimulated += (100 - currentSimulated) * 0.05; // 渐近增长
          const simulatedValue = startProgress + (currentSimulated / 100) * (endProgress - startProgress) * 0.9;
          setProgress(Math.round(simulatedValue));
        }, 300);

        const formData = new FormData();
        formData.append('file', file);
        formData.append('target_format', targetFormat);
        formData.append('keep_name', keepName.toString());
        formData.append('device_pref', devicePref);

        const response = await axios.post(`${API_BASE_URL}/convert`, formData, {
          responseType: 'blob',
        });

        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;

        let outputName = '';
        const contentDisposition = response.headers['content-disposition'];
        if (contentDisposition) {
          const match = contentDisposition.match(/filename="(.+)"/);
          if (match) outputName = match[1];
        }

        if (!outputName) {
          outputName = file.name.replace(/\.[^/.]+$/, "") + targetFormat;
        }

        link.setAttribute('download', outputName);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);

        successCount++;
        // 文件处理完，立即跳到该文件的 100% 进度
        setProgress(Math.round(endProgress));
      }

      if (simulatedInterval) clearInterval(simulatedInterval);
      setStatus('success');
      setMessage(t('success'));
      setFiles([]);
    } catch (err) {
      if (simulatedInterval) clearInterval(simulatedInterval);
      console.error('Conversion error:', err);
      
      let errorDetail = '';
      if (err.response && err.response.data instanceof Blob) {
        // Since responseType is 'blob', we need to read it to get the JSON error
        const reader = new FileReader();
        reader.onload = () => {
          try {
            const errorJson = JSON.parse(reader.result);
            console.error('Backend error:', errorJson.error);
            setMessage(errorJson.error || t('error'));
          } catch (e) {
            setMessage(t('error'));
          }
        };
        reader.readAsText(err.response.data);
      } else {
        setMessage(t('error'));
      }
      
      setStatus('error');
    }
 finally {
      // 延迟关闭上传状态以展示 100% 进度
      setTimeout(() => {
        setIsUploading(false);
        setProgress(0);
      }, 600);
    }
  };


  if (!systemStatus.ready && !isFetching) {
    return (
      <div className="app-container setup-mode">
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-card setup-card"
        >
          <div className="setup-header">
            <Settings className="setup-icon spin-slow" size={48} />
            <h1>{t('setupTitle')}</h1>
            <p>{t('setupSubtitle')}</p>
          </div>

          <div className="setup-body">
            <div className="dependency-list">
              <div className="dep-item success">
                <CheckCircle size={20} />
                <span>Python {t('setupReady')}</span>
              </div>
              {systemStatus.missing_deps.map((dep, idx) => (
                <div key={idx} className="dep-item error">
                  <AlertTriangle size={20} />
                  <span>{dep}</span>
                </div>
              ))}
            </div>

            <div className="setup-footer">
              <div className="setup-status-msg">
                <Loader className="spinner" size={20} />
                <span>{t('setupFix')}</span>
              </div>
              <button 
                className="button outline" 
                onClick={getFormats}
                disabled={isFetching}
              >
                {isFetching ? t('fetching') : t('refresh')}
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="app-container">
      {/* 语言切换器 */}
      <div className="language-selector">
        <div
          className={`lang-option ${language === 'zh' ? 'active' : ''}`}
          onClick={() => setLanguage('zh')}
        >
          中
        </div>
        <div className="lang-divider"></div>
        <div
          className={`lang-option ${language === 'en' ? 'active' : ''}`}
          onClick={() => setLanguage('en')}
        >
          EN
        </div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        className="glass-card"
      >
        <div className="title-section">
          <motion.h1
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            {t('title')}
          </motion.h1>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            {t('subtitle')}
          </motion.p>
        </div>

        {/* 文件上传区 */}
        <div
          className={`drop-zone ${isDragging ? 'dragging' : ''} ${files.length > 0 ? 'compact' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => document.getElementById('file-input').click()}
          style={files.length > 0 ? { padding: '2rem' } : {}}
        >
          <input
            id="file-input"
            type="file"
            multiple
            hidden
            onChange={onFileChange}
          />
          <div className="icon-wrapper">
            {status === 'uploading' ? (
              <Loader2 className="animate-spin" size={files.length > 0 ? 24 : 32} />
            ) : (
              <Upload size={files.length > 0 ? 24 : 32} />
            )}
          </div>
          {files.length === 0 ? (
            <div style={{ textAlign: 'center' }}>
              <p style={{ marginBottom: '4px', fontWeight: '600' }}>{t('dropFiles')}</p>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t('browseFiles')}</p>
            </div>
          ) : (
            <p style={{ fontWeight: '600', fontSize: '0.9rem' }}>{t('addMore')}</p>
          )}
        </div>

        {/* 文件列表 */}
        <AnimatePresence>
          {files.length > 0 && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="file-list"
            >
              {files.map((file, idx) => (
                <motion.div
                  key={`${file.name}-${idx}`}
                  layout
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="file-item"
                >
                  <div className="file-info">
                    <FileText size={16} color="var(--accent-color)" />
                    <span className="file-name">{file.name}</span>
                  </div>
                  <button className="remove-file" onClick={(e) => {
                    e.stopPropagation();
                    removeFile(idx);
                  }}>
                    <X size={14} />
                  </button>
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        {/* 格式选择面板 */}
        <AnimatePresence>
          {files.length > 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="format-selection-panel"
            >
              <motion.div 
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.1 }}
                className="search-box"
              >
                <Search size={18} className="search-icon" />
                <input
                  type="text"
                  placeholder={t('searchPlaceholder')}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </motion.div>

              {/* 分类标签栏 */}
              <motion.div 
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.2 }}
                className="category-tabs"
              >
                <motion.button 
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className={`cat-chip ${selectedCategory === 'catAll' ? 'active' : ''}`}
                  onClick={() => setSelectedCategory('catAll')}
                >
                  {t('catAll')}
                </motion.button>
                {Object.keys(CATEGORIES).map((catKey, idx) => (
                  <motion.button
                    key={catKey}
                    initial={{ x: -10, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    transition={{ delay: 0.2 + idx * 0.05 }}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className={`cat-chip ${selectedCategory === catKey ? 'active' : ''}`}
                    onClick={() => setSelectedCategory(catKey)}
                  >
                    {t(catKey)}
                  </motion.button>
                ))}
              </motion.div>

              <div className="format-grid">
                {isFetching && Object.keys(supportedFormats).length === 0 ? (
                  <p style={{ gridColumn: '1/-1', textAlign: 'center', fontSize: '0.85rem', color: 'var(--text-secondary)', padding: '1rem' }}>
                    <Loader2 className="animate-spin" size={16} /> {t('fetching')}
                  </p>
                ) : filteredFormats.length > 0 ? (
                  filteredFormats.map(fmt => (
                    <motion.div
                      key={fmt}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      className={`format-tag ${targetFormat === fmt ? 'selected' : ''}`}
                      onClick={() => setTargetFormat(fmt)}
                    >
                      {fmt.replace('.', '').toUpperCase()}
                    </motion.div>
                  ))
                ) : (
                  <p style={{ gridColumn: '1/-1', textAlign: 'center', fontSize: '0.85rem', color: 'var(--text-secondary)', padding: '1rem' }}>
                    {Object.keys(supportedFormats).length === 0 ? t('noFormats') : (availableTargetFormats.length === 0 ? t('noCommonFormats') : t('noMatches'))}
                  </p>
                )}
              </div>

              <div className="options-container">
                <div
                  className={`toggle-container ${keepName ? 'active' : ''}`}
                  onClick={() => setKeepName(!keepName)}
                >
                  <div className="toggle-switch"></div>
                  <span className="toggle-label">{t('keepOriginalName')}</span>
                </div>
                
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginLeft: 'auto', fontSize: '0.85rem' }}>
                    <Settings2 size={14} color="var(--text-secondary)" />
                    <span style={{ color: 'var(--text-secondary)' }}>加速模式:</span>
                    <select 
                      value={devicePref} 
                      onChange={(e) => setDevicePref(e.target.value)}
                      style={{ 
                        padding: '4px 8px', 
                        borderRadius: '6px', 
                        border: '1px solid var(--border-color)', 
                        background: 'var(--bg-secondary)', 
                        color: 'var(--text-primary)',
                        outline: 'none',
                        cursor: 'pointer'
                      }}
                    >
                      <option value="auto">自动选择</option>
                      <option value="cpu">强制 CPU</option>
                      <option value="gpu">强制 GPU</option>
                    </select>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <button
          className="button"
          disabled={files.length === 0 || !targetFormat || status === 'uploading'}
          onClick={handleConvert}
          style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
        >
          {status === 'uploading' ? (
            <>
              <Loader2 className="animate-spin" size={18} />
              <span>{t('converting')}</span>
            </>
          ) : (
            <>
              <span>{t('convertTo')} {targetFormat ? targetFormat.replace('.', '').toUpperCase() : t('defaultTarget')}</span>
              <ChevronRight size={18} />
            </>
          )}
        </button>

        <AnimatePresence>
          {isUploading && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="progress-wrapper"
            >
              <div className="progress-info">
                <span>{t('converting')}</span>
                <span>{progress}%</span>
              </div>
              <div className="progress-track">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  transition={{ duration: 0.3 }}
                  className="progress-fill"
                />
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {message && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className={`status-message ${status === 'success' ? 'status-success' : status === 'error' ? 'status-error' : ''}`}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                {status === 'success' && <Download size={18} />}
                {status === 'error' && <XCircle size={18} />}
                <span>{message}</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}

export default App;
