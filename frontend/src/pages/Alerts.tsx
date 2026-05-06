import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { alertsApi } from '../services/api'
import { Plus, AlertTriangle, CheckCircle } from 'lucide-react'

export default function Alerts() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    name: '', description: '', metric_name: '', condition: '>', threshold: 0, severity: 'medium'
  })

  const { data: alerts } = useQuery({
    queryKey: ['alerts'],
    queryFn: alertsApi.getAll,
  })

  const { data: rules } = useQuery({
    queryKey: ['alertRules'],
    queryFn: alertsApi.getRules,
  })

  const createRuleMutation = useMutation({
    mutationFn: alertsApi.createRule,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alertRules'] })
      setShowForm(false)
      setFormData({ name: '', description: '', metric_name: '', condition: '>', threshold: 0, severity: 'medium' })
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createRuleMutation.mutate({
      ...formData,
      threshold: parseFloat(formData.threshold.toString())
    })
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Alerts</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700"
        >
          <Plus className="w-4 h-4" /> Create Rule
        </button>
      </div>

      {showForm && (
        <div className="bg-white p-6 rounded-lg shadow mb-6">
          <h2 className="text-lg font-semibold mb-4">New Alert Rule</h2>
          <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-4">
            <input
              placeholder="Rule Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="border p-2 rounded"
              required
            />
            <select
              value={formData.severity}
              onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
              className="border p-2 rounded"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
            <input
              placeholder="Metric Name"
              value={formData.metric_name}
              onChange={(e) => setFormData({ ...formData, metric_name: e.target.value })}
              className="border p-2 rounded"
              required
            />
            <select
              value={formData.condition}
              onChange={(e) => setFormData({ ...formData, condition: e.target.value })}
              className="border p-2 rounded"
            >
              <option value=">">Greater than</option>
              <option value="<">Less than</option>
              <option value="=">Equal to</option>
            </select>
            <input
              type="number"
              placeholder="Threshold"
              value={formData.threshold}
              onChange={(e) => setFormData({ ...formData, threshold: parseFloat(e.target.value) })}
              className="border p-2 rounded"
              required
            />
            <input
              placeholder="Description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="border p-2 rounded"
            />
            <button type="submit" className="bg-blue-600 text-white py-2 rounded col-span-2 hover:bg-blue-700">
              Create Rule
            </button>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h2 className="text-lg font-semibold mb-4">Alert Rules</h2>
          <div className="space-y-3">
            {rules?.map((rule: any) => (
              <div key={rule.id} className="bg-white p-4 rounded-lg shadow">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold">{rule.name}</h3>
                    <p className="text-sm text-gray-500">{rule.metric_name} {rule.condition} {rule.threshold}</p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs ${
                    rule.severity === 'critical' ? 'bg-red-100 text-red-700' :
                    rule.severity === 'high' ? 'bg-orange-100 text-orange-700' :
                    'bg-yellow-100 text-yellow-700'
                  }`}>
                    {rule.severity}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h2 className="text-lg font-semibold mb-4">Recent Alerts</h2>
          <div className="space-y-3">
            {alerts?.slice(0, 10).map((alert: any) => (
              <div key={alert.id} className="bg-white p-4 rounded-lg shadow flex items-start gap-3">
                {alert.status === 'active' ? (
                  <AlertTriangle className="w-5 h-5 text-red-500" />
                ) : (
                  <CheckCircle className="w-5 h-5 text-green-500" />
                )}
                <div>
                  <h3 className="font-semibold">{alert.metric_name}</h3>
                  <p className="text-sm text-gray-500">
                    Value: {alert.metric_value} (threshold: {alert.threshold})
                  </p>
                  <p className="text-xs text-gray-400">{new Date(alert.triggered_at).toLocaleString()}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
