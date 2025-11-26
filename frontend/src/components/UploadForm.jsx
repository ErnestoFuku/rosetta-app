import { useState } from 'react';
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function UploadForm() {
  const [spectrum, setSpectrum] = useState(null);
  const [conclusion, setConclusion] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  // Nivel predefinido para filtrado (1-4)
  const [filterPreset, setFilterPreset] = useState(2); // 1=Muy estricto, 2=Estricto, 3=Moderado, 4=Permisivo
  
  // Valores predefinidos para cada nivel de filtrado
  const filterPresets = {
    1: { // Muy estricto
      name: 'Muy Estricto',
      headDrop: 15,
      madMultiplierRTOF: 5,
      cpsThresholdRTOF: 3,
      madMultiplierDFMS: 5,
      cpsThresholdDFMS: 5e3
    },
    2: { // Estricto (default original)
      name: 'Estricto',
      headDrop: 10,
      madMultiplierRTOF: 10,
      cpsThresholdRTOF: 5,
      madMultiplierDFMS: 8,
      cpsThresholdDFMS: 1e4
    },
    3: { // Moderado
      name: 'Moderado',
      headDrop: 8,
      madMultiplierRTOF: 15,
      cpsThresholdRTOF: 8,
      madMultiplierDFMS: 12,
      cpsThresholdDFMS: 2e4
    },
    4: { // Permisivo
      name: 'Permisivo',
      headDrop: 5,
      madMultiplierRTOF: 20,
      cpsThresholdRTOF: 12,
      madMultiplierDFMS: 15,
      cpsThresholdDFMS: 5e4
    }
  };

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.tab')) {
      setError('Por favor, selecciona un archivo .tab');
      return;
    }

    setLoading(true);
    setError('');
    setSpectrum(null);
    setConclusion('');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('filter_level', 'high'); // Siempre alto grado
    
    // Enviar parámetros del preset seleccionado
    const preset = filterPresets[filterPreset];
    formData.append('head_drop', preset.headDrop.toString());
    formData.append('mad_multiplier_rtof', preset.madMultiplierRTOF.toString());
    formData.append('cps_threshold_rtof', preset.cpsThresholdRTOF.toString());
    formData.append('mad_multiplier_dfms', preset.madMultiplierDFMS.toString());
    formData.append('cps_threshold_dfms', preset.cpsThresholdDFMS.toString());

    try {
      const { data } = await axios.post(`${API_URL}/process`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setSpectrum(data.spectrum);
      
      // Asegurarse de que conclusion sea siempre un string
      let conclusionText = '';
      if (data.conclusion) {
        console.log('Tipo de conclusión recibida:', typeof data.conclusion);
        console.log('Contenido de conclusión:', data.conclusion);
        
        if (typeof data.conclusion === 'string') {
          conclusionText = data.conclusion;
        } else if (typeof data.conclusion === 'object') {
          // Si es un objeto, intentar extraer el texto
          // Manejar estructura {id, type, status, content, role}
          if (data.conclusion.content) {
            const content = data.conclusion.content;
            if (typeof content === 'string') {
              conclusionText = content;
            } else if (Array.isArray(content)) {
              // Si content es un array, buscar el texto
              for (const item of content) {
                if (typeof item === 'string') {
                  conclusionText = item;
                  break;
                } else if (item && typeof item === 'object' && item.text) {
                  conclusionText = item.text;
                  break;
                }
              }
              if (!conclusionText) {
                conclusionText = JSON.stringify(content, null, 2);
              }
            } else if (typeof content === 'object') {
              // Si content es un objeto anidado
              if (content.text) {
                conclusionText = content.text;
              } else {
                conclusionText = JSON.stringify(content, null, 2);
              }
            } else {
              conclusionText = String(content);
            }
          } else if (data.conclusion.text) {
            conclusionText = data.conclusion.text;
          } else if (data.conclusion.message) {
            conclusionText = typeof data.conclusion.message === 'string' 
              ? data.conclusion.message 
              : JSON.stringify(data.conclusion.message, null, 2);
          } else {
            // Si no podemos extraer texto, mostrar el objeto formateado
            conclusionText = JSON.stringify(data.conclusion, null, 2);
          }
        } else {
          conclusionText = String(data.conclusion);
        }
      }
      
      console.log('Conclusión final (tipo):', typeof conclusionText);
      setConclusion(conclusionText);
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Error desconocido';
      setError(`Error al procesar el archivo: ${errorMessage}`);
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const chartData = spectrum ? {
    labels: spectrum.map(p => p.x.toFixed(2)),
    datasets: [
      {
        label: 'Intensidad (cps)',
        data: spectrum.map(p => p.cps),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        fill: true,
        tension: 0.4,
        pointRadius: 0,
      },
    ],
  } : null;

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top',
      },
      title: {
        display: true,
        text: 'Espectro de Masas',
        font: {
          size: 18,
          weight: 'bold'
        }
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'm/z (masa/carga)',
          font: {
            size: 14,
            weight: 'bold'
          }
        },
      },
      y: {
        title: {
          display: true,
          text: 'Intensidad (cps)',
          font: {
            size: 14,
            weight: 'bold'
          }
        },
        beginAtZero: true,
      },
    },
  };

  return (
    <div style={{ 
      padding: '2rem', 
      maxWidth: '1200px', 
      margin: '0 auto',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderRadius: '12px',
      boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)'
    }}>
      <h1 style={{ marginBottom: '2rem', color: '#333' }}>Analizador de Espectros Rosetta</h1>
      
      {/* Niveles predefinidos de filtrado */}
      <div style={{
        marginBottom: '2rem',
        padding: '1.5rem',
        backgroundColor: '#e8f5e9',
        borderRadius: '8px',
        border: '1px solid #4CAF50'
      }}>
        <h3 style={{ marginTop: 0, marginBottom: '1rem', color: '#2e7d32' }}>
          📊 Nivel de Filtrado Predefinido
        </h3>
        
        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
          {[1, 2, 3, 4].map((level) => {
            const preset = filterPresets[level];
            const isSelected = filterPreset === level;
            return (
              <button
                key={level}
                type="button"
                onClick={() => setFilterPreset(level)}
                disabled={loading}
                style={{
                  flex: '1',
                  minWidth: '150px',
                  padding: '1rem',
                  backgroundColor: isSelected ? '#4CAF50' : '#f5f5f5',
                  color: isSelected ? 'white' : '#333',
                  border: `2px solid ${isSelected ? '#2e7d32' : '#ddd'}`,
                  borderRadius: '8px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  fontSize: '0.95rem',
                  fontWeight: isSelected ? 'bold' : 'normal',
                  transition: 'all 0.3s ease',
                  opacity: loading ? 0.6 : 1,
                  boxShadow: isSelected ? '0 2px 8px rgba(76, 175, 80, 0.3)' : 'none'
                }}
              >
                <div style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>{preset.name}</div>
                <div style={{ fontSize: '0.8rem', opacity: 0.9 }}>
                  MAD RTOF: {preset.madMultiplierRTOF} | CPS: {preset.cpsThresholdRTOF}
                </div>
              </button>
            );
          })}
        </div>
        
        {/* Mostrar detalles del preset seleccionado */}
        <div style={{
          padding: '1rem',
          backgroundColor: 'white',
          borderRadius: '6px',
          border: '1px solid #c8e6c9'
        }}>
          <h4 style={{ marginTop: 0, marginBottom: '0.75rem', color: '#2e7d32' }}>
            Configuración: {filterPresets[filterPreset].name}
          </h4>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', fontSize: '0.9rem' }}>
            <div>
              <strong>Filas descartadas:</strong> {filterPresets[filterPreset].headDrop}
            </div>
            <div>
              <strong>MAD RTOF:</strong> {filterPresets[filterPreset].madMultiplierRTOF}
            </div>
            <div>
              <strong>CPS RTOF:</strong> {filterPresets[filterPreset].cpsThresholdRTOF}
            </div>
            <div>
              <strong>MAD DFMS:</strong> {filterPresets[filterPreset].madMultiplierDFMS}
            </div>
            <div>
              <strong>CPS DFMS:</strong> {filterPresets[filterPreset].cpsThresholdDFMS >= 1e3 
                ? filterPresets[filterPreset].cpsThresholdDFMS.toExponential(1) 
                : filterPresets[filterPreset].cpsThresholdDFMS}
            </div>
          </div>
          <p style={{ 
            fontSize: '0.85rem', 
            color: '#666', 
            marginTop: '0.75rem',
            marginBottom: 0,
            fontStyle: 'italic'
          }}>
            {filterPreset === 1 && 'Filtrado muy agresivo - elimina la mayoría de outliers y artefactos. Ideal para señales muy limpias.'}
            {filterPreset === 2 && 'Filtrado estándar (original) - balance entre limpieza y conservación de datos. Recomendado para uso general.'}
            {filterPreset === 3 && 'Filtrado moderado - mantiene más señales débiles pero reales. Útil cuando se necesitan más datos.'}
            {filterPreset === 4 && 'Filtrado permisivo - conserva la mayoría de los datos. Útil para análisis detallados de señales débiles.'}
          </p>
        </div>
      </div>
      
      <div style={{ marginBottom: '2rem' }}>
        <label
          htmlFor="file-input"
          style={{
            display: 'inline-block',
            padding: '0.75rem 1.5rem',
            backgroundColor: '#4CAF50',
            color: 'white',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontSize: '1rem',
            fontWeight: 'bold',
            opacity: loading ? 0.6 : 1,
            transition: 'all 0.3s ease'
          }}
        >
          {loading ? 'Procesando...' : 'Seleccionar archivo .tab'}
        </label>
        <input
          id="file-input"
          type="file"
          accept=".tab"
          onChange={handleFileChange}
          style={{ display: 'none' }}
          disabled={loading}
        />
      </div>

      {loading && (
        <div style={{ padding: '1rem', textAlign: 'center' }}>
          <p style={{ color: '#666' }}>Procesando archivo...</p>
        </div>
      )}

      {error && (
        <div
          style={{
            padding: '1rem',
            backgroundColor: '#ffebee',
            color: '#c62828',
            borderRadius: '4px',
            marginBottom: '1rem',
            border: '1px solid #ef5350'
          }}
        >
          {error}
        </div>
      )}

      {spectrum && (
        <div style={{ marginBottom: '2rem' }}>
          <div style={{ height: '400px', marginBottom: '1rem', backgroundColor: 'white', padding: '1rem', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
            <Line data={chartData} options={chartOptions} />
          </div>
        </div>
      )}

      {conclusion && (
        <div
          style={{
            padding: '1.5rem',
            backgroundColor: '#f5f5f5',
            borderRadius: '8px',
            border: '1px solid #ddd',
            textAlign: 'left'
          }}
        >
          <h2 style={{ marginTop: 0, marginBottom: '1rem', color: '#333' }}>Conclusión</h2>
          <pre
            style={{
              whiteSpace: 'pre-wrap',
              wordWrap: 'break-word',
              fontFamily: 'inherit',
              fontSize: '1rem',
              lineHeight: '1.6',
              margin: 0,
              color: '#444'
            }}
          >
            {conclusion}
          </pre>
        </div>
      )}
    </div>
  );
}

export default UploadForm;

