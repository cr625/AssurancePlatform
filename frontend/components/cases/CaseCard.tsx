'use client'

import React, { useState } from 'react'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
// import { AssuranceCase } from '@/types'
import Link from 'next/link'
import moment from 'moment'
import { Trash2 } from 'lucide-react'
import { AlertModal } from '@/components/modals/alertModal'
import { useParams, useRouter } from 'next/navigation'
import { useLoginToken } from '@/hooks/useAuth'

interface CaseCardProps {
  assuranceCase: any
}

const CaseCard = ({ assuranceCase } : CaseCardProps) => {
  const { id, name, description, created_date, image } = assuranceCase
  const [ token ] = useLoginToken()
  const params = useParams();
  const router = useRouter()

  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const onDelete = async () => {
    try {
      setLoading(true);

      const requestOptions: RequestInit = {
        headers: {
          Authorization: `Token ${token}`,
        },
        method: "DELETE",
      };

      const response = await fetch(`http://localhost:8000/api/cases/${assuranceCase.id}/`, requestOptions)
      if(response.ok) {
        window.location.reload()
      }
    } catch (error: any) {
      console.log('ERROR!!!!', error)
    } finally {
      setLoading(false);
      setOpen(false);
    }
  }

  return (
    <>
    <Link href={`/case/${assuranceCase.id}`} className='group relative'>
      <Card className='flex flex-col justify-start items-start group-hover:bg-indigo-500/5 transition-all h-full'>
        <CardHeader className='flex-1'>
          <img src='https://images.unsplash.com/photo-1708844897353-649da595a3f2?q=80&w=3132&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D' alt='' className='rounded-md mb-4' />
          <CardTitle>{name}</CardTitle>
          <CardDescription className='text-slate-900 dark:text-white'>{description}</CardDescription>
        </CardHeader>
        <CardFooter className="flex justify-end text-xs text-gray-500 dark:text-gray-300">
          <p>Created on: {moment(created_date).format('DD/MM/YYYY')}</p>
        </CardFooter>
        <button disabled={loading} onClick={() => setOpen(true)} className='absolute hidden group-hover:block top-4 right-4 bg-rose-500 text-white p-2 rounded-md shadow-lg'>
          <Trash2 className='w-4 h-4' />
        </button>
      </Card>
    </Link>
    <AlertModal
      isOpen={open} 
      onClose={() => setOpen(false)}
      onConfirm={onDelete}
      loading={loading}
    />
    </>
  )
}

export default CaseCard
