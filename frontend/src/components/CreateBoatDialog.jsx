import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { useAuth } from '@/hooks/useAuth'
import { Loader2 } from 'lucide-react'

export default function CreateBoatDialog({ open, onOpenChange, onBoatCreated }) {
  const [formData, setFormData] = useState({
    name: '',
    boat_type: '',
    class_name: '',
    year_built: '',
    loa: '',
    lwl: '',
    beam: '',
    draft: '',
    displacement: '',
    sail_area: '',
    keel_type: '',
    rig_type: '',
    hull_material: '',
    rating_system: '',
    rating_value: '',
    crew_size: '',
    notes: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  
  const { getAuthHeaders, API_BASE } = useAuth()

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSelectChange = (name, value) => {
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    // Convert numeric fields
    const submitData = {
      ...formData,
      year_built: formData.year_built ? parseInt(formData.year_built) : null,
      loa: formData.loa ? parseFloat(formData.loa) : null,
      lwl: formData.lwl ? parseFloat(formData.lwl) : null,
      beam: formData.beam ? parseFloat(formData.beam) : null,
      draft: formData.draft ? parseFloat(formData.draft) : null,
      displacement: formData.displacement ? parseFloat(formData.displacement) : null,
      sail_area: formData.sail_area ? parseFloat(formData.sail_area) : null,
      crew_size: formData.crew_size ? parseInt(formData.crew_size) : null
    }

    try {
      const response = await fetch(`${API_BASE}/boats`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders()
        },
        body: JSON.stringify(submitData)
      })

      const data = await response.json()

      if (response.ok) {
        onBoatCreated(data.boat)
        // Reset form
        setFormData({
          name: '',
          boat_type: '',
          class_name: '',
          year_built: '',
          loa: '',
          lwl: '',
          beam: '',
          draft: '',
          displacement: '',
          sail_area: '',
          keel_type: '',
          rig_type: '',
          hull_material: '',
          rating_system: '',
          rating_value: '',
          crew_size: '',
          notes: ''
        })
      } else {
        setError(data.error)
      }
    } catch (error) {
      setError('Network error while creating boat')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Add New Boat</DialogTitle>
          <DialogDescription>
            Create a new boat profile to start building polar models
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Basic Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Basic Information</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="name">Boat Name *</Label>
                <Input
                  id="name"
                  name="name"
                  required
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="e.g., Aurelius"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="boat_type">Boat Type *</Label>
                <Select onValueChange={(value) => handleSelectChange('boat_type', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select boat type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="monohull">Monohull</SelectItem>
                    <SelectItem value="catamaran">Catamaran</SelectItem>
                    <SelectItem value="trimaran">Trimaran</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="class_name">Class/Design</Label>
                <Input
                  id="class_name"
                  name="class_name"
                  value={formData.class_name}
                  onChange={handleChange}
                  placeholder="e.g., J/105, Farr 40"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="year_built">Year Built</Label>
                <Input
                  id="year_built"
                  name="year_built"
                  type="number"
                  value={formData.year_built}
                  onChange={handleChange}
                  placeholder="e.g., 2010"
                />
              </div>
            </div>
          </div>

          {/* Specifications */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Specifications</h3>
            
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="loa">LOA (m)</Label>
                <Input
                  id="loa"
                  name="loa"
                  type="number"
                  step="0.1"
                  value={formData.loa}
                  onChange={handleChange}
                  placeholder="10.5"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="lwl">LWL (m)</Label>
                <Input
                  id="lwl"
                  name="lwl"
                  type="number"
                  step="0.1"
                  value={formData.lwl}
                  onChange={handleChange}
                  placeholder="9.2"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="beam">Beam (m)</Label>
                <Input
                  id="beam"
                  name="beam"
                  type="number"
                  step="0.1"
                  value={formData.beam}
                  onChange={handleChange}
                  placeholder="3.5"
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="draft">Draft (m)</Label>
                <Input
                  id="draft"
                  name="draft"
                  type="number"
                  step="0.1"
                  value={formData.draft}
                  onChange={handleChange}
                  placeholder="2.1"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="displacement">Displacement (kg)</Label>
                <Input
                  id="displacement"
                  name="displacement"
                  type="number"
                  value={formData.displacement}
                  onChange={handleChange}
                  placeholder="3500"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="sail_area">Sail Area (m²)</Label>
                <Input
                  id="sail_area"
                  name="sail_area"
                  type="number"
                  step="0.1"
                  value={formData.sail_area}
                  onChange={handleChange}
                  placeholder="45.5"
                />
              </div>
            </div>
          </div>

          {/* Configuration */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Configuration</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="keel_type">Keel Type</Label>
                <Select onValueChange={(value) => handleSelectChange('keel_type', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select keel type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="fin">Fin Keel</SelectItem>
                    <SelectItem value="full">Full Keel</SelectItem>
                    <SelectItem value="wing">Wing Keel</SelectItem>
                    <SelectItem value="centerboard">Centerboard</SelectItem>
                    <SelectItem value="daggerboard">Daggerboard</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="rig_type">Rig Type</Label>
                <Select onValueChange={(value) => handleSelectChange('rig_type', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select rig type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="sloop">Sloop</SelectItem>
                    <SelectItem value="cutter">Cutter</SelectItem>
                    <SelectItem value="ketch">Ketch</SelectItem>
                    <SelectItem value="yawl">Yawl</SelectItem>
                    <SelectItem value="schooner">Schooner</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="hull_material">Hull Material</Label>
                <Select onValueChange={(value) => handleSelectChange('hull_material', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select hull material" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="fiberglass">Fiberglass</SelectItem>
                    <SelectItem value="carbon">Carbon Fiber</SelectItem>
                    <SelectItem value="aluminum">Aluminum</SelectItem>
                    <SelectItem value="steel">Steel</SelectItem>
                    <SelectItem value="wood">Wood</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="crew_size">Crew Size</Label>
                <Input
                  id="crew_size"
                  name="crew_size"
                  type="number"
                  value={formData.crew_size}
                  onChange={handleChange}
                  placeholder="6"
                />
              </div>
            </div>
          </div>

          {/* Racing Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Racing Information</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="rating_system">Rating System</Label>
                <Select onValueChange={(value) => handleSelectChange('rating_system', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select rating system" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="IRC">IRC</SelectItem>
                    <SelectItem value="ORC">ORC</SelectItem>
                    <SelectItem value="PHRF">PHRF</SelectItem>
                    <SelectItem value="Portsmouth">Portsmouth</SelectItem>
                    <SelectItem value="One Design">One Design</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="rating_value">Rating Value</Label>
                <Input
                  id="rating_value"
                  name="rating_value"
                  value={formData.rating_value}
                  onChange={handleChange}
                  placeholder="e.g., 1.045, 150"
                />
              </div>
            </div>
          </div>

          {/* Notes */}
          <div className="space-y-2">
            <Label htmlFor="notes">Notes</Label>
            <Textarea
              id="notes"
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              placeholder="Additional notes about the boat..."
              rows={3}
            />
          </div>

          <div className="flex justify-end space-x-2">
            <Button 
              type="button" 
              variant="outline" 
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating...
                </>
              ) : (
                'Create Boat'
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}

